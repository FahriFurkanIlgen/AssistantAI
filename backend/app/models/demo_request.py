from beanie import Document
from pydantic import EmailStr
from datetime import datetime
from typing import Optional


class DemoRequest(Document):
    name: str
    business_name: str
    sector: str = "general"
    phone: str
    email: EmailStr
    city: Optional[str] = None
    message: Optional[str] = None
    status: str = "pending"          # pending | contacted | converted | rejected
    notes: Optional[str] = None      # admin internal notes
    created_at: datetime = None
    updated_at: datetime = None

    def __init__(self, **data):
        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = datetime.utcnow()
        if "updated_at" not in data or data["updated_at"] is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)

    class Settings:
        name = "demo_requests"
