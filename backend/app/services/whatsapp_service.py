"""
WhatsApp Cloud API bridge.

Each business connects their own Meta App + WABA. We talk to
https://graph.facebook.com/v20.0/{phone_number_id}/messages with their
permanent access token. Incoming messages arrive at our webhook endpoint
which dispatches them through the same AI pipeline as the web chat.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx

from app.models.business import Business
from app.models.conversation import Conversation, Message
from app.services import customer_service, knowledge_service
from app.services.ai_service import AIService
from app.services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v20.0"
# How long a single text send is allowed to take before we give up.
_SEND_TIMEOUT = 15.0
# Hard cap on outbound text length (WhatsApp accepts up to 4096 chars).
_MAX_TEXT = 3800


def _normalize_to(number: str) -> str:
    """Meta expects E.164 without '+' or spaces."""
    return "".join(ch for ch in (number or "") if ch.isdigit())


async def send_text(business: Business, to: str, text: str) -> dict:
    """Send a plain text message via WhatsApp Cloud API.

    Raises httpx.HTTPStatusError on Meta-side errors so the caller can
    surface a useful message (e.g. the test-send button).
    """
    cfg = business.whatsapp
    if not cfg or not cfg.phone_number_id or not cfg.access_token:
        raise RuntimeError("WhatsApp yapılandırması eksik")

    payload = {
        "messaging_product": "whatsapp",
        "to": _normalize_to(to),
        "type": "text",
        "text": {"body": (text or "")[:_MAX_TEXT]},
    }
    url = f"{GRAPH_BASE}/{cfg.phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {cfg.access_token}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=_SEND_TIMEOUT) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def find_business_by_phone_number_id(pnid: str) -> Optional[Business]:
    if not pnid:
        return None
    # Beanie can't query embedded fields by dot path with == cleanly across
    # versions, so use a raw filter.
    return await Business.find_one({"whatsapp.phone_number_id": pnid})


def verify_webhook(business: Business, mode: str, token: str, challenge: str) -> Optional[str]:
    """Meta webhook handshake — return challenge if token matches."""
    cfg = business.whatsapp
    if not cfg or not cfg.verify_token:
        return None
    if mode == "subscribe" and token == cfg.verify_token:
        return challenge
    return None


def _extract_text_messages(payload: dict) -> list[dict]:
    """Flatten Meta's nested webhook payload into a list of
    {phone_number_id, from, text, message_id, language}.

    We currently only handle inbound *text* messages. Status callbacks
    (delivered/read) and other types are ignored.
    """
    out: list[dict] = []
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            metadata = value.get("metadata") or {}
            pnid = metadata.get("phone_number_id")
            for msg in value.get("messages") or []:
                if msg.get("type") != "text":
                    continue
                body = (msg.get("text") or {}).get("body")
                if not body:
                    continue
                out.append({
                    "phone_number_id": pnid,
                    "from": msg.get("from"),
                    "text": body,
                    "message_id": msg.get("id"),
                })
    return out


async def _process_one(business: Business, sender: str, text: str) -> str:
    """Run the AI pipeline for a single inbound WhatsApp message and
    return the assistant reply. Mirrors the web-chat router but trimmed.
    """
    session_id = f"wa:{_normalize_to(sender)}"

    conversation = await Conversation.find_one(
        Conversation.business_id == str(business.id),
        Conversation.session_id == session_id,
        Conversation.status == "active",
    )
    if not conversation:
        conversation = Conversation(
            business_id=str(business.id),
            session_id=session_id,
            channel="whatsapp",
            language="tr",
            customer_phone=sender,
        )
        await conversation.insert()
    elif conversation.channel != "whatsapp":
        conversation.channel = "whatsapp"

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

    # Customer memory: WA already gives us a phone number, so this almost
    # always resolves on returning customers.
    matched_customer = await customer_service.find_by_phone(str(business.id), sender)
    customer_memory = (
        customer_service.format_memory_block(matched_customer)
        if matched_customer
        else ""
    )

    ai = AIService(
        business,
        tool_executor,
        kb_search=kb_pre_retrieve,
        business_facts=business_facts,
        customer_memory=customer_memory,
    )
    reply = await ai.process_message(
        conversation=conversation,
        user_message=text,
        language=conversation.language or "tr",
    )

    if matched_customer is not None:
        asyncio.create_task(
            customer_service.maybe_update_summary(matched_customer, conversation)
        )

    return reply


async def handle_incoming(business: Business, payload: dict) -> None:
    """Process every inbound text message in a Meta webhook payload and
    send a reply back via WhatsApp. Designed to be awaited from a
    background task — the webhook route must respond 200 fast.
    """
    messages = _extract_text_messages(payload)
    for m in messages:
        # Defensive: ignore messages destined for some other tenant.
        if m["phone_number_id"] and business.whatsapp.phone_number_id \
                and m["phone_number_id"] != business.whatsapp.phone_number_id:
            logger.warning(
                "WA payload phone_number_id mismatch for slug=%s", business.slug
            )
            continue
        try:
            reply = await _process_one(business, m["from"], m["text"])
        except Exception:
            logger.exception("WA inbound processing failed")
            reply = (
                "Şu an küçük bir aksaklık var, birkaç dakika sonra "
                "tekrar yazabilir misiniz?"
            )
        try:
            await send_text(business, m["from"], reply)
        except httpx.HTTPStatusError as e:
            logger.error("WA send failed: %s — %s", e, e.response.text)
        except Exception:
            logger.exception("WA send raised")
