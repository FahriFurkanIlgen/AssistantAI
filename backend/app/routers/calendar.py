"""
Calendar Router - Google OAuth2 flow and calendar management.
"""
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from datetime import datetime

from app.models.business import Business
from app.core.auth import get_current_user
from app.services.calendar_service import get_authorization_url, exchange_code_for_tokens
from app.config import settings

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# Temporary in-memory state store (use Redis in production)
_oauth_states: dict = {}


@router.get("/connect")
async def connect_google(current_business: Business = Depends(get_current_user)):
    """Initiate Google OAuth2 flow."""
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = str(current_business.id)

    auth_url = get_authorization_url(state=state)
    return {"auth_url": auth_url}


@router.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    """Handle Google OAuth2 callback."""
    business_id = _oauth_states.pop(state, None)
    if not business_id:
        raise HTTPException(status_code=400, detail="Geçersiz OAuth state")

    business = await Business.get(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    try:
        tokens = exchange_code_for_tokens(code)
        business.google_access_token = tokens["access_token"]
        business.google_refresh_token = tokens["refresh_token"]
        if tokens.get("expiry"):
            business.google_token_expiry = datetime.fromisoformat(tokens["expiry"])
        business.updated_at = datetime.utcnow()
        await business.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token alınamadı: {str(e)}")

    # Redirect to frontend settings page
    frontend_url = settings.ALLOWED_ORIGINS[0]
    return RedirectResponse(url=f"{frontend_url}/dashboard/settings?google=connected")


@router.delete("/disconnect")
async def disconnect_google(current_business: Business = Depends(get_current_user)):
    """Remove Google Calendar connection."""
    current_business.google_access_token = None
    current_business.google_refresh_token = None
    current_business.google_token_expiry = None
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return {"message": "Google Calendar bağlantısı kaldırıldı"}
