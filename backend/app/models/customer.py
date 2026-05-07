from beanie import Document
from pydantic import EmailStr
from typing import Optional
from datetime import datetime


class Customer(Document):
    business_id: str
    name: str
    phone: str
    email: Optional[EmailStr] = None
    language_preference: str = "tr"
    total_appointments: int = 0
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "customers"
        indexes = ["business_id", "phone"]
