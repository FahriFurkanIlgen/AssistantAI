from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, time


class WorkingHours(BaseModel):
    start: str = "09:00"  # HH:MM format
    end: str = "18:00"
    is_open: bool = True


class WorkingSchedule(BaseModel):
    monday: WorkingHours = WorkingHours()
    tuesday: WorkingHours = WorkingHours()
    wednesday: WorkingHours = WorkingHours()
    thursday: WorkingHours = WorkingHours()
    friday: WorkingHours = WorkingHours()
    saturday: WorkingHours = WorkingHours(is_open=False)
    sunday: WorkingHours = WorkingHours(is_open=False)


class ServiceItem(BaseModel):
    name: str
    name_tr: str
    duration_minutes: int = 60
    price: Optional[float] = None
    description: Optional[str] = None


class Business(Document):
    name: str
    slug: str  # URL-friendly unique identifier
    email: EmailStr
    hashed_password: str
    phone: Optional[str] = None

    # Sector: tattoo | doctor | beauty | general
    sector: str = "tattoo"

    # Location
    address: Optional[str] = None
    city: Optional[str] = None

    # AI Configuration
    ai_persona_name: str = "Asistan"
    ai_welcome_message_tr: str = "Merhaba! Size nasıl yardımcı olabilirim?"
    ai_welcome_message_en: str = "Hello! How can I help you today?"
    custom_ai_instructions: Optional[str] = None

    # Services offered
    services: List[ServiceItem] = []

    # Working schedule
    working_schedule: WorkingSchedule = WorkingSchedule()

    # Appointment duration default (minutes)
    default_appointment_duration: int = 60

    # Social media
    instagram_handle: Optional[str] = None  # e.g. "blackinktattoo" (without @)

    # Google Calendar
    google_calendar_id: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_access_token: Optional[str] = None
    google_token_expiry: Optional[datetime] = None

    # Status
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "businesses"
        indexes = ["slug", "email"]
