"""
WhatsApp Router — Meta Cloud API webhook + admin helpers.

Setup flow (per business):
  1. Owner opens Settings → WhatsApp, fills phone_number_id /
     access_token / verify_token / display_phone and saves.
  2. In Meta App dashboard → WhatsApp → Configuration:
       Callback URL: https://<your-domain>/api/whatsapp/webhook/<slug>
       Verify Token: <same verify_token as above>
       Webhook fields: messages
  3. Meta hits GET /webhook/{slug} once for the handshake; we echo
     hub.challenge if the token matches.
  4. Inbound messages then POST to the same path.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from pydantic import BaseModel
import httpx

from app.core.auth import get_current_user
from app.models.business import Business
from app.services import whatsapp_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.get("/webhook/{slug}")
async def webhook_verify(
    slug: str,
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """Meta webhook handshake. Must return the raw challenge integer-string
    as text/plain when the verify_token matches.
    """
    business = await Business.find_one(Business.slug == slug)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    result = whatsapp_service.verify_webhook(
        business, hub_mode or "", hub_verify_token or "", hub_challenge or ""
    )
    if result is None:
        raise HTTPException(status_code=403, detail="Verify token mismatch")
    # Meta wants plain text echo of challenge
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(result)


@router.post("/webhook/{slug}")
async def webhook_incoming(
    slug: str,
    request: Request,
    background: BackgroundTasks,
):
    """Receive inbound WhatsApp messages. We always 200 quickly and do the
    AI work in the background — Meta retries aggressively on slow webhooks.
    """
    business = await Business.find_one(Business.slug == slug)
    if not business or not business.whatsapp or not business.whatsapp.enabled:
        # 200 anyway so Meta doesn't keep retrying a misconfigured tenant.
        return {"ok": True, "ignored": True}
    try:
        payload = await request.json()
    except Exception:
        return {"ok": True, "ignored": "bad_json"}
    background.add_task(whatsapp_service.handle_incoming, business, payload)
    return {"ok": True}


# ── Authed helpers (used by the dashboard Settings UI) ──────────────────────
class TestSendRequest(BaseModel):
    to: str
    text: Optional[str] = None


@router.post("/test-send")
async def test_send(
    req: TestSendRequest,
    current_business: Business = Depends(get_current_user),
):
    """Send a one-off test message from the connected WhatsApp number.

    Notes for the user:
      - The target number must have opened a conversation with your WABA
        in the last 24h, OR you must use a pre-approved template.
        For development this means: message your own WABA number first
        from your personal WhatsApp, then click "Test mesajı gönder".
    """
    if not current_business.whatsapp or not current_business.whatsapp.enabled:
        raise HTTPException(status_code=400, detail="WhatsApp etkin değil")
    if not current_business.whatsapp.phone_number_id or not current_business.whatsapp.access_token:
        raise HTTPException(status_code=400, detail="WhatsApp yapılandırması eksik")

    body = req.text or "Merhaba! AssistantAI WhatsApp köprünüz çalışıyor 👋"
    try:
        result = await whatsapp_service.send_text(current_business, req.to, body)
    except httpx.HTTPStatusError as e:
        detail = "Meta API hatası"
        try:
            data = e.response.json()
            err = data.get("error") or {}
            msg = err.get("message")
            if msg:
                detail = f"Meta: {msg}"
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=detail)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("WA test-send failed: %s", e)
        raise HTTPException(status_code=500, detail="Test mesajı gönderilemedi")
    return {"ok": True, "result": result}


@router.get("/status")
async def get_status(current_business: Business = Depends(get_current_user)):
    """Return the masked WhatsApp config so the dashboard can pre-fill the
    form without leaking the full access token.
    """
    cfg = current_business.whatsapp
    if not cfg:
        return {"enabled": False}

    def _mask(s: Optional[str]) -> Optional[str]:
        if not s:
            return None
        if len(s) <= 8:
            return "•" * len(s)
        return s[:4] + "…" + s[-4:]

    return {
        "enabled": cfg.enabled,
        "phone_number_id": cfg.phone_number_id,
        "display_phone": cfg.display_phone,
        "access_token_preview": _mask(cfg.access_token),
        "verify_token_set": bool(cfg.verify_token),
        # The webhook URL the owner should paste into Meta
        "webhook_path": f"/api/whatsapp/webhook/{current_business.slug}",
    }
