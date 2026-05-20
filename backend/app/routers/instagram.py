"""
Instagram Router — Meta Graph API + Messenger Platform webhook + admin helpers.

Setup flow (per business):
  1. IG hesabı Professional + Facebook Page'e bağlı olmalı.
  2. Meta App'te Instagram Graph API + Messenger ürünleri eklenir.
  3. Owner dashboard → Settings → Instagram: ig_user_id, page_id,
     access_token (Page Access Token), verify_token, app_secret doldurur.
  4. Meta App → Webhooks → Instagram:
       Callback URL:  https://<your-domain>/api/instagram/webhook/<slug>
       Verify Token:  <yukarıdaki verify_token>
       Subscribe to:  messages, messaging_postbacks
  5. Meta GET /webhook/{slug} ile el sıkışır; biz hub.challenge'ı echo'larız.
  6. Inbound DM'ler aynı path'e POST gelir.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.business import Business
from app.services import instagram_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/instagram", tags=["instagram"])


# ── Webhook: handshake ─────────────────────────────────────────────────────
@router.get("/webhook/{slug}")
async def webhook_verify(
    slug: str,
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    business = await Business.find_one(Business.slug == slug)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    result = instagram_service.verify_webhook(
        business, hub_mode or "", hub_verify_token or "", hub_challenge or ""
    )
    if result is None:
        raise HTTPException(status_code=403, detail="Verify token mismatch")
    return PlainTextResponse(result)


# ── Webhook: incoming DM ───────────────────────────────────────────────────
@router.post("/webhook/{slug}")
async def webhook_incoming(
    slug: str,
    request: Request,
    background: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
):
    business = await Business.find_one(Business.slug == slug)
    if not business or not business.instagram or not business.instagram.enabled:
        # 200 anyway so Meta doesn't keep retrying misconfigured tenants.
        return {"ok": True, "ignored": True}

    raw = await request.body()
    if not instagram_service.verify_signature(business, raw, x_hub_signature_256):
        logger.warning("IG webhook signature mismatch for slug=%s", slug)
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = await request.json()
    except Exception:
        return {"ok": True, "ignored": "bad_json"}

    background.add_task(instagram_service.handle_incoming, business, payload)
    return {"ok": True}


# ── Public: portfolio via Graph API (fallback to scraping ayrı endpoint) ──
@router.get("/{slug}/portfolio")
async def public_portfolio(slug: str, limit: int = 12):
    """Public endpoint — chat widget bunu çağırıp portfolyo grid'i çizebilir.

    Graph API yapılandırılmamışsa boş `posts: []` döner; çağıran taraf
    `/api/chat/{slug}/portfolio` (scrape) endpoint'ine fallback yapabilir.
    """
    business = await Business.find_one(Business.slug == slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    cfg = business.instagram
    if not cfg or not cfg.enabled or not cfg.access_token or not cfg.ig_user_id:
        return {"source": "none", "posts": []}

    posts = await instagram_service.fetch_media(business, limit=limit)
    return {
        "source": "graph_api",
        "ig_user_id": cfg.ig_user_id,
        "ig_username": cfg.ig_username,
        "posts": posts,
    }


# ── Authed helpers (dashboard Settings UI) ─────────────────────────────────
class TestSendRequest(BaseModel):
    to: str  # IGSID (recipient's Instagram-scoped user id)
    text: Optional[str] = None


@router.post("/test-send")
async def test_send(
    req: TestSendRequest,
    current_business: Business = Depends(get_current_user),
):
    """Tek seferlik test DM gönderir.

    Önemli: alıcı IGSID, son 24 saat içinde işletmeye DM atmış olmalı
    (Messenger 24-hour window kuralı). Aksi halde Meta hata döner.
    """
    cfg = current_business.instagram
    if not cfg or not cfg.enabled:
        raise HTTPException(status_code=400, detail="Instagram etkin değil")
    if not cfg.access_token or not cfg.ig_user_id:
        raise HTTPException(status_code=400, detail="Instagram yapılandırması eksik")

    body = req.text or "Merhaba! AssistantAI Instagram köprünüz çalışıyor 👋"
    try:
        result = await instagram_service.send_text(current_business, req.to, body)
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
        logger.exception("IG test-send failed: %s", e)
        raise HTTPException(status_code=500, detail="Test mesajı gönderilemedi")
    return {"ok": True, "result": result}


@router.post("/refresh-media")
async def refresh_media(current_business: Business = Depends(get_current_user)):
    """Smoke test — Graph API'den son medya kayıtlarını çek ve sayısını döndür."""
    cfg = current_business.instagram
    if not cfg or not cfg.access_token or not cfg.ig_user_id:
        raise HTTPException(status_code=400, detail="Instagram yapılandırması eksik")
    posts = await instagram_service.fetch_media(current_business, limit=12)
    return {"count": len(posts), "posts": posts[:3]}  # sadece ilk 3'ü önizleme


@router.get("/status")
async def get_status(current_business: Business = Depends(get_current_user)):
    cfg = current_business.instagram
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
        "ig_user_id": cfg.ig_user_id,
        "page_id": cfg.page_id,
        "ig_username": cfg.ig_username,
        "access_token_preview": _mask(cfg.access_token),
        "verify_token_set": bool(cfg.verify_token),
        "app_secret_set": bool(cfg.app_secret),
        "webhook_path": f"/api/instagram/webhook/{current_business.slug}",
    }
