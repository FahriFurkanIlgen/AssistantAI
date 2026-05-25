from beanie import Document
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Reservation(Document):
    business_id: str

    # Table (denormalized for display without extra lookup)
    table_id: str          # primary table (or first of combo)
    table_number: str      # e.g. "5"  (or "3+6" for combos)
    table_section: str = ""  # e.g. "iç", "dış", "vip"

    # Multi-table combo support
    table_ids: List[str] = []        # all table IDs (empty = single, use table_id)
    combined_capacity: Optional[int] = None  # sum of capacities when combo

    # Customer
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    party_size: int = 2

    # Timing
    date: str              # YYYY-MM-DD
    shift_name: str        # e.g. "Akşam"
    shift_start: str       # HH:MM
    shift_end: str         # HH:MM

    # Extra
    special_requests: Optional[str] = None
    notes: Optional[str] = None

    # confirmed | seated | completed | cancelled | no_show
    status: str = "confirmed"

    # web | whatsapp | instagram | manual
    channel: str = "web"
    language: str = "tr"

    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "reservations"
        indexes = ["business_id", "date", "table_id", "status"]
