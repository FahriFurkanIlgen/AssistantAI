"""
Chat Router - SSE streaming chat endpoint for the AI assistant.
"""
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

from app.models.business import Business
from app.models.conversation import Conversation, Message
from app.services.ai_service import AIService
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "tr"


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

    # Process message
    reply = await ai_service.process_message(
        conversation=conversation,
        user_message=request.message,
        language=request.language or conversation.language,
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
    }
