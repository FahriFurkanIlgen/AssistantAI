import uuid
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


class InstagramConfig(BaseModel):
    """Per-business Instagram API (Instagram Login flow) configuration.

    Meta'nın 2024+ yeni "Instagram API with Instagram Login" akışı kullanılır.
    Facebook Page ve Page Access Token GEREKMEZ.

    Setup adımları (işletme sahibi):
      1. Instagram hesabı Professional (Business veya Creator) olmalı.
      2. developers.facebook.com → Create App → use case:
         "Manage messaging & content on Instagram" seç.
      3. Permissions: `instagram_business_basic`,
         `instagram_business_manage_messages`,
         (opsiyonel) `instagram_business_manage_comments`,
         `instagram_business_content_publish`.
      4. App'in Instagram ayarlarından Instagram User Access Token üret
         (kalıcı / long-lived) ve buraya yapıştır.
      5. ig_user_id otomatik /me endpoint'inden çekilir (save sırasında).

    Saklanan alanlar:
      - ig_user_id   : Instagram Business Account ID (otomatik doldurulur).
      - page_id      : (deprecated, eski Messenger akışı için; kullanılmıyor)
      - access_token : Instagram User Access Token (kalıcı).
      - verify_token : Webhook el sıkışmasında kullanıcı tarafından seçilen string.
      - app_secret   : (opsiyonel) X-Hub-Signature-256 HMAC doğrulaması için.
      - ig_username  : İsim göstermek için (handle, "@" olmadan).

    Webhook callback URL'i:
      https://<your-domain>/api/instagram/webhook/<slug>
    Subscription field'ları: `messages`, `messaging_postbacks`.
    """
    enabled: bool = False
    ig_user_id: Optional[str] = None
    page_id: Optional[str] = None
    access_token: Optional[str] = None
    verify_token: Optional[str] = None
    app_secret: Optional[str] = None
    ig_username: Optional[str] = None


# ── Restaurant Reservation Models ────────────────────────────────────────────

class RestaurantTable(BaseModel):
    """A single table in the restaurant floor plan."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: str              # e.g. "1", "A3"
    name: Optional[str] = None  # optional friendly name e.g. "Pencere Kenarı"
    capacity: int = 4
    # section: iç | dış | vip | teras | bar
    section: str = "iç"
    # shape for floor plan rendering: square | round | rectangle
    shape: str = "square"
    is_active: bool = True
    # Floor plan position (percentage of canvas width/height, 0–100)
    x: float = 10.0
    y: float = 10.0
    width: float = 8.0   # % of canvas
    height: float = 8.0  # % of canvas


class DiningShift(BaseModel):
    """A meal period during which reservations can be made."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str           # e.g. "Öğle", "Akşam"
    start_time: str     # HH:MM
    end_time: str       # HH:MM
    is_active: bool = True
    # Comma-separated day names or ["all"]
    days: List[str] = Field(default_factory=lambda: [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ])


class RestaurantConfig(BaseModel):
    """Restaurant-specific configuration embedded in Business."""
    enabled: bool = False
    tables: List[RestaurantTable] = Field(default_factory=list)
    shifts: List[DiningShift] = Field(default_factory=list)
    # How long a reservation holds a table (minutes)
    reservation_duration: int = 90
    max_party_size: int = 20
    # How many days ahead reservations can be made
    reservation_window_days: int = 30


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

    # Instagram Graph API + Messenger Platform bridge (per-business)
    instagram: InstagramConfig = InstagramConfig()

    # Restaurant reservation system
    restaurant: "RestaurantConfig" = Field(default_factory=lambda: RestaurantConfig())

    # Status
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "businesses"
        indexes = ["slug", "email"]
