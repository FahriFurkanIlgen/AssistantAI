from beanie import Document
from pydantic import EmailStr
from typing import Optional, List
from datetime import datetime

from app.models.business import WorkingSchedule


class StaffMember(Document):
    business_id: str
    name: str
    email: EmailStr
    hashed_password: str
    phone: Optional[str] = None
    bio: Optional[str] = None

    # Services this staff member provides (subset of business services by name)
    service_names: List[str] = []

    # Independent working schedule (overrides business schedule for this staff)
    working_schedule: WorkingSchedule = WorkingSchedule()

    # Per-staff Google Calendar integration
    google_calendar_id: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_access_token: Optional[str] = None
    google_token_expiry: Optional[datetime] = None

    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "staff_members"
        indexes = ["business_id", "email"]
