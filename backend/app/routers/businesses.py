"""
Business Router - Profile and settings management.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.business import Business, WorkingHours, WorkingSchedule, ServiceItem
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/business", tags=["business"])


class UpdateBusinessRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    ai_persona_name: Optional[str] = None
    ai_welcome_message_tr: Optional[str] = None
    ai_welcome_message_en: Optional[str] = None
    custom_ai_instructions: Optional[str] = None
    default_appointment_duration: Optional[int] = None
    instagram_handle: Optional[str] = None
    services: Optional[List[ServiceItem]] = None
    working_schedule: Optional[WorkingSchedule] = None


@router.get("/profile")
async def get_profile(current_business: Business = Depends(get_current_user)):
    return {
        "id": str(current_business.id),
        "name": current_business.name,
        "slug": current_business.slug,
        "email": current_business.email,
        "sector": current_business.sector,
        "phone": current_business.phone,
        "address": current_business.address,
        "city": current_business.city,
        "ai_persona_name": current_business.ai_persona_name,
        "ai_welcome_message_tr": current_business.ai_welcome_message_tr,
        "ai_welcome_message_en": current_business.ai_welcome_message_en,
        "custom_ai_instructions": current_business.custom_ai_instructions,
        "services": [s.model_dump() for s in current_business.services],
        "working_schedule": current_business.working_schedule.model_dump(),
        "default_appointment_duration": current_business.default_appointment_duration,
        "instagram_handle": current_business.instagram_handle,
        "google_connected": current_business.google_refresh_token is not None,
    }


@router.patch("/profile")
async def update_profile(
    req: UpdateBusinessRequest,
    current_business: Business = Depends(get_current_user),
):
    update_data = req.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(current_business, key, value)
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return {"message": "Profil güncellendi"}


@router.get("/public/{slug}")
async def get_public_profile(slug: str):
    business = await Business.find_one(Business.slug == slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    return {
        "name": business.name,
        "slug": business.slug,
        "sector": business.sector,
        "city": business.city,
        "services": [s.model_dump() for s in business.services],
        "ai_persona_name": business.ai_persona_name,
    }
