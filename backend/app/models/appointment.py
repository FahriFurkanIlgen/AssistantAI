from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Appointment(Document):
    business_id: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None

    # Service details
    service_name: str
    service_name_tr: Optional[str] = None
    notes: Optional[str] = None

    # Timing
    start_time: datetime
    end_time: datetime
    duration_minutes: int = 60

    # Status: pending | confirmed | cancelled | completed
    status: str = "confirmed"

    # Assigned staff member (optional)
    staff_id: Optional[str] = None
    staff_name: Optional[str] = None

    # Google Calendar event ID
    google_event_id: Optional[str] = None

    # Language customer used: tr | en
    language: str = "tr"

    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "appointments"
        indexes = ["business_id", "start_time", "status"]
