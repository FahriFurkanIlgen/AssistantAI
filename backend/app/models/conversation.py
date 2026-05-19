from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    role: str  # user | assistant | system | tool
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list] = None
    timestamp: datetime = datetime.utcnow()


class Conversation(Document):
    business_id: str
    session_id: str  # anonymous session identifier
    channel: str = "web"  # web | whatsapp | instagram | ...
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    language: str = "tr"
    messages: List[Message] = []
    appointment_id: Optional[str] = None  # linked appointment if created
    status: str = "active"  # active | completed | abandoned
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "conversations"
        indexes = ["business_id", "session_id"]
