from beanie import Document
from pydantic import BaseModel, EmailStr, Field
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


class WhatsAppConfig(BaseModel):
    """Per-business WhatsApp Cloud API configuration.

    The business creates their own Meta App + WABA, then pastes:
      - phone_number_id  (from Meta dashboard → WhatsApp → API setup)
      - access_token     (System User permanent token, scoped to whatsapp_business_messaging)
      - verify_token     (any random string they pick; Meta echoes it back during webhook setup)
      - display_phone    (the user-facing E.164 number)
    The webhook callback URL they paste into Meta is:
      https://<your-domain>/api/whatsapp/webhook/<slug>
    """
    enabled: bool = False
    phone_number_id: Optional[str] = None
    access_token: Optional[str] = None
    verify_token: Optional[str] = None
    display_phone: Optional[str] = None


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
    ai_welcome_message_ru: str = "Здравствуйте! Чем я могу вам помочь?"
    ai_welcome_message_de: str = "Hallo! Wie kann ich Ihnen helfen?"
    ai_welcome_message_ar: str = "مرحبًا! كيف يمكنني مساعدتك؟"
    custom_ai_instructions: Optional[str] = None

    # Suggested questions shown as starter chips in the chat widget.
    # When empty, no chips are rendered (no built-in fallback).
    suggested_questions: List[str] = Field(default_factory=list)

    # TTS voice for the assistant — OpenAI tts-1 voices.
    # Allowed: alloy, echo, fable, onyx, nova, shimmer
    tts_voice: str = "nova"

    # Services offered
    services: List[ServiceItem] = []

    # Working schedule
    working_schedule: WorkingSchedule = WorkingSchedule()

    # Appointment duration default (minutes)
    default_appointment_duration: int = 60

    # Social media
    instagram_handle: Optional[str] = None  # e.g. "blackinktattoo" (without @)

    # Brand logo (data URL veya https URL). Chat ekranındaki avatar
    # dairesinde gösterilir. Boşsa persona harf/emoji fallback'i kullanılır.
    logo_url: Optional[str] = None

    # Chat ekranı varsayılan teması. "light" (default) veya "dark".
    # Kullanıcı widget içindeki toggle ile o oturum için override edebilir.
    chat_theme: str = "light"

    # Google Calendar
    google_calendar_id: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_access_token: Optional[str] = None
    google_token_expiry: Optional[datetime] = None

    # WhatsApp Cloud API bridge (per-business)
    whatsapp: WhatsAppConfig = WhatsAppConfig()

    # Status
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "businesses"
        indexes = ["slug", "email"]
