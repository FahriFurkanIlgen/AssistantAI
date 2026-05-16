"""
Chat Router - SSE streaming chat endpoint for the AI assistant.
"""
import logging
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

from openai import AuthenticationError, APIError, RateLimitError

from app.models.business import Business
from app.models.conversation import Conversation, Message
from app.services.ai_service import AIService
from app.services.appointment_service import AppointmentService
from app.services.vision_service import is_instagram_url, extract_og_image, fetch_instagram_portfolio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "tr"
    image_base64: Optional[str] = None   # data:image/...;base64,... (file upload)
    image_url: Optional[str] = None      # Instagram post URL or direct image URL


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    appointment_created: bool = False
    appointment_id: Optional[str] = None


@router.post("/{business_slug}", response_model=ChatResponse)
async def chat(business_slug: str, request: ChatRequest):
    business = await Business.find_one(Business.slug == business_slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    # Get or create conversation
    session_id = request.session_id or str(uuid.uuid4())
    conversation = await Conversation.find_one(
        Conversation.session_id == session_id,
        Conversation.status == "active",
    )

    if not conversation:
        conversation = Conversation(
            business_id=str(business.id),
            session_id=session_id,
            language=request.language or "tr",
        )
        await conversation.insert()

    # Build services
    appt_service = AppointmentService(business)
    ai_service = AIService(business, appt_service.execute_tool)

    # Resolve image: Instagram link → extract og:image; base64 → use as-is
    resolved_image: Optional[str] = None
    if request.image_base64:
        resolved_image = request.image_base64
    elif request.image_url:
        if is_instagram_url(request.image_url):
            resolved_image = await extract_og_image(request.image_url)
        else:
            resolved_image = request.image_url

    # Process message
    try:
        reply = await ai_service.process_message(
            conversation=conversation,
            user_message=request.message,
            language=request.language or conversation.language,
            image=resolved_image,
        )
    except AuthenticationError:
        logger.error("OpenAI API key is invalid or missing")
        raise HTTPException(
            status_code=503,
            detail="AI servisi şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        )
    except RateLimitError:
        logger.warning("OpenAI rate limit hit")
        raise HTTPException(
            status_code=429,
            detail="Çok fazla istek. Lütfen birkaç saniye sonra tekrar deneyin.",
        )
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=502,
            detail="AI servisinde geçici bir sorun var. Lütfen tekrar deneyin.",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Bir hata oluştu. Lütfen tekrar deneyin.",
        )

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        appointment_created=conversation.appointment_id is not None,
        appointment_id=conversation.appointment_id,
    )


@router.get("/{business_slug}/welcome")
async def get_welcome(business_slug: str, lang: str = "tr"):
    business = await Business.find_one(Business.slug == business_slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    message = (
        business.ai_welcome_message_tr
        if lang == "tr"
        else business.ai_welcome_message_en
    )
    return {
        "business_name": business.name,
        "persona_name": business.ai_persona_name,
        "welcome_message": message,
        "sector": business.sector,
        "instagram_handle": business.instagram_handle,
    }


@router.get("/{business_slug}/portfolio")
async def get_portfolio(business_slug: str):
    """Return Instagram portfolio posts for the business."""
    business = await Business.find_one(Business.slug == business_slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    if not business.instagram_handle:
        return {"instagram_handle": None, "posts": [], "instagram_url": None}

    handle = business.instagram_handle.lstrip("@")
    posts = await fetch_instagram_portfolio(handle)
    return {
        "instagram_handle": handle,
        "instagram_url": f"https://www.instagram.com/{handle}/",
        "posts": posts,
    }
