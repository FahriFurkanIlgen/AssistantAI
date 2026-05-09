from beanie import Document
from datetime import datetime, timedelta
from typing import Optional


class OtpCode(Document):
    appointment_id: str
    email: str
    code: str                          # 6-digit string
    expires_at: datetime
    used: bool = False
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "otp_codes"
        indexes = ["appointment_id", "email"]

    @classmethod
    def generate(cls, appointment_id: str, email: str, code: str, ttl_minutes: int = 10) -> "OtpCode":
        return cls(
            appointment_id=appointment_id,
            email=email,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
        )

    def is_valid(self) -> bool:
        return not self.used and datetime.utcnow() < self.expires_at
