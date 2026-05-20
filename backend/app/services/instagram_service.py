"""
Instagram API with Instagram Login bridge (per-business).

Meta'nın yeni (2024+) "Instagram API with Instagram Login" akışı:
  - Base: https://graph.instagram.com/v21.0  (graph.facebook.com değil)
  - Token: Instagram User Access Token (Page token değil; FB Page gerekmez)
  - Permissions: instagram_business_basic, instagram_business_manage_messages

Aynı token ile iki şey:
  1. Media (portfolyo) okuma — GET /me/media
  2. DM gönderme/alma — POST /me/messages

Webhook payload (DM):
  {
    "object": "instagram",
    "entry": [{
      "id": "<ig_user_id>", "time": ...,
      "messaging": [{
        "sender":   {"id": "<igsid>"},
        "recipient":{"id": "<ig_user_id>"},
        "timestamp": ...,
        "message":  {"mid": "...", "text": "merhaba"}
      }]
    }]
  }
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
from typing import List, Optional

import httpx

from app.models.business import Business
from app.models.conversation import Conversation
from app.services import customer_service, knowledge_service
from app.services.ai_service import AIService
from app.services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.instagram.com/v21.0"
_SEND_TIMEOUT = 15.0
# Instagram DM text limit ~ 1000 chars (vs 4096 for WA). Keep generous margin.
_MAX_TEXT = 950

_MEDIA_FIELDS = (
    "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp"
)


# ── Outbound DM ────────────────────────────────────────────────────────────
async def send_text(business: Business, recipient_id: str, text: str) -> dict:
    """Send a DM via Instagram API (Instagram Login flow)."""
    cfg = business.instagram
    if not cfg or not cfg.access_token:
        raise RuntimeError("Instagram yapılandırması eksik")

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": (text or "")[:_MAX_TEXT]},
    }
    url = f"{GRAPH_BASE}/me/messages"
    params = {"access_token": cfg.access_token}
    async with httpx.AsyncClient(timeout=_SEND_TIMEOUT) as client:
        resp = await client.post(url, json=payload, params=params)
        resp.raise_for_status()
        return resp.json()


# ── Identity (otomatik ig_user_id keşfi) ──────────────────────────────────
async def fetch_identity(access_token: str) -> dict:
    """GET /me with the IG User Access Token → {id, username}.

    Settings save akışında, kullanıcı yeni token yapıştırdığında ig_user_id'yi
    otomatik doldurmak için kullanılır.
    """
    if not access_token:
        return {}
    url = f"{GRAPH_BASE}/me"
    params = {"fields": "id,username", "access_token": access_token}
    try:
        async with httpx.AsyncClient(timeout=_SEND_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json() or {}
    except Exception as e:
        logger.warning("IG identity fetch failed: %s", e)
        return {}


# ── Media (portfolyo) ──────────────────────────────────────────────────────
async def fetch_media(business: Business, limit: int = 12) -> List[dict]:
    """Return latest Instagram posts via Graph API.

    Item dict shape (normalized to match vision_service.fetch_instagram_portfolio):
      {shortcode: str|None, url: str, thumbnail: str|None,
       caption: str|None, media_type: str, timestamp: str}
    """
    cfg = business.instagram
    if not cfg or not cfg.access_token:
        return []

    url = f"{GRAPH_BASE}/me/media"
    params = {
        "fields": _MEDIA_FIELDS,
        "limit": max(1, min(limit, 25)),
        "access_token": cfg.access_token,
    }
    try:
        async with httpx.AsyncClient(timeout=_SEND_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        logger.warning("IG media fetch failed: %s — %s", e, e.response.text[:200])
        return []
    except Exception as e:
        logger.warning("IG media fetch error: %s", e)
        return []

    items: List[dict] = []
    for it in data.get("data") or []:
        permalink = it.get("permalink") or ""
        shortcode = None
        if permalink:
            parts = permalink.rstrip("/").split("/")
            if parts:
                shortcode = parts[-1]
        # Videos: media_url is mp4, thumbnail_url is the preview frame.
        # Images: thumbnail_url is absent; media_url is the image itself.
        media_type = it.get("media_type") or "IMAGE"
        if media_type == "VIDEO":
            thumb = it.get("thumbnail_url") or it.get("media_url")
        else:
            thumb = it.get("media_url") or it.get("thumbnail_url")
        items.append({
            "shortcode": shortcode,
            "url": permalink,
            "thumbnail": thumb,
            "caption": it.get("caption"),
            "media_type": media_type,
            "timestamp": it.get("timestamp"),
        })
    return items


# ── Webhook helpers ────────────────────────────────────────────────────────
def verify_webhook(business: Business, mode: str, token: str, challenge: str) -> Optional[str]:
    cfg = business.instagram
    if not cfg or not cfg.verify_token:
        return None
    if mode == "subscribe" and token == cfg.verify_token:
        return challenge
    return None


def verify_signature(business: Business, raw_body: bytes, header_value: Optional[str]) -> bool:
    """Optional X-Hub-Signature-256 HMAC check. Returns True if not configured
    or if signature matches. Returns False only when app_secret is set AND
    signature is missing/invalid.
    """
    cfg = business.instagram
    if not cfg or not cfg.app_secret:
        return True
    if not header_value or not header_value.startswith("sha256="):
        return False
    expected = hmac.new(
        cfg.app_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    provided = header_value.split("=", 1)[1].strip()
    return hmac.compare_digest(expected, provided)


def _extract_text_messages(payload: dict) -> List[dict]:
    """Flatten IG DM webhook into {sender_id, text, message_id, ig_user_id}.

    Ignores echo messages (sent by us), reactions, attachments-only, etc.
    """
    out: List[dict] = []
    if payload.get("object") != "instagram":
        return out
    for entry in payload.get("entry") or []:
        for ev in entry.get("messaging") or []:
            msg = ev.get("message") or {}
            if msg.get("is_echo"):
                continue
            text = (msg.get("text") or "").strip()
            if not text:
                continue
            sender = (ev.get("sender") or {}).get("id")
            recipient = (ev.get("recipient") or {}).get("id")
            if not sender:
                continue
            out.append({
                "sender_id": sender,
                "ig_user_id": recipient,
                "text": text,
                "message_id": msg.get("mid"),
            })
    return out


# ── Inbound pipeline ───────────────────────────────────────────────────────
async def find_business_by_ig_user_id(ig_user_id: str) -> Optional[Business]:
    if not ig_user_id:
        return None
    return await Business.find_one({"instagram.ig_user_id": ig_user_id})


async def _process_one(business: Business, sender_id: str, text: str) -> str:
    """Run the AI pipeline for one inbound IG DM. Mirrors whatsapp_service."""
    session_id = f"ig:{sender_id}"

    conversation = await Conversation.find_one(
        Conversation.business_id == str(business.id),
        Conversation.session_id == session_id,
        Conversation.status == "active",
    )
    if not conversation:
        conversation = Conversation(
            business_id=str(business.id),
            session_id=session_id,
            channel="instagram",
            language="tr",
        )
        await conversation.insert()
    elif conversation.channel != "instagram":
        conversation.channel = "instagram"

    appt_service = AppointmentService(business)

    async def tool_executor(fn_name: str, fn_args: dict, conv):
        if fn_name == "search_knowledge_base":
            results = await knowledge_service.search(
                business_id=str(business.id),
                query=fn_args.get("query", ""),
                top_k=fn_args.get("top_k", 4),
            )
            return {"results": results}
        return await appt_service.execute_tool(fn_name, fn_args, conv)

    async def kb_pre_retrieve(query: str):
        hits = await knowledge_service.search(
            business_id=str(business.id),
            query=query,
            top_k=4,
            min_score=0.30,
        )
        try:
            best = max((h["score"] for h in hits), default=0.0)
            if best < 0.45 and knowledge_service.looks_like_question(query):
                await knowledge_service.log_gap(
                    business_id=str(business.id),
                    question=query,
                    language=conversation.language,
                    session_id=session_id,
                    best_score=best,
                )
        except Exception:
            pass
        return hits

    business_facts = await knowledge_service.build_business_facts(business)

    ai = AIService(
        business,
        tool_executor,
        kb_search=kb_pre_retrieve,
        business_facts=business_facts,
        customer_memory="",
    )
    reply = await ai.process_message(
        conversation=conversation,
        user_message=text,
        language=conversation.language or "tr",
    )
    return reply


async def handle_incoming(business: Business, payload: dict) -> None:
    """Process every inbound text DM and reply via the Graph API.

    Designed to be awaited from a BackgroundTask — the webhook itself must
    return 200 fast or Meta will keep retrying.
    """
    cfg = business.instagram
    messages = _extract_text_messages(payload)
    for m in messages:
        # Defensive multi-tenant guard: drop messages addressed to another IG account.
        if cfg.ig_user_id and m["ig_user_id"] and m["ig_user_id"] != cfg.ig_user_id:
            logger.warning(
                "IG payload ig_user_id mismatch for slug=%s", business.slug
            )
            continue
        try:
            reply = await _process_one(business, m["sender_id"], m["text"])
        except Exception:
            logger.exception("IG inbound processing failed")
            reply = (
                "Şu an küçük bir aksaklık var, birkaç dakika içinde "
                "tekrar yazabilir misiniz?"
            )
        try:
            await send_text(business, m["sender_id"], reply)
        except httpx.HTTPStatusError as e:
            logger.error("IG send failed: %s — %s", e, e.response.text)
        except Exception:
            logger.exception("IG send raised")
