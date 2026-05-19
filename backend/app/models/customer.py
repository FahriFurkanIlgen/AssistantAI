from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class CustomerPreferences(BaseModel):
    """Free-form preference slots the AI / owner can fill in."""
    preferred_staff: Optional[str] = None       # e.g. "Ahmet Usta"
    preferred_staff_id: Optional[str] = None
    preferred_times: Optional[str] = None       # e.g. "Cumartesi öğleden sonra"
    favorite_services: List[str] = Field(default_factory=list)
    allergies: Optional[str] = None
    notes: Optional[str] = None                 # owner-facing free text


class Customer(Document):
    business_id: str
    name: str
    phone: str                                  # normalized canonical form
    phone_display: Optional[str] = None         # original as entered
    email: Optional[EmailStr] = None
    language_preference: str = "tr"

    total_appointments: int = 0
    total_conversations: int = 0

    # ── Memory layer ────────────────────────────────────────────────
    memory_summary: Optional[str] = None        # rolling LLM summary (2-3 sentences)
    preferences: CustomerPreferences = Field(default_factory=CustomerPreferences)
    tags: List[str] = Field(default_factory=list)  # e.g. ["vegan", "hassas cilt"]

    last_seen_at: Optional[datetime] = None
    last_summary_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customers"
        indexes = ["business_id", "phone"]
