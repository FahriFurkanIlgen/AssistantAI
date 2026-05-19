"""
Customers Router - access the durable customer memory layer.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.auth import get_current_user
from app.models.business import Business
from app.models.customer import Customer, CustomerPreferences
from app.models.appointment import Appointment
from app.services import customer_service

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _serialize(c: Customer, *, with_memory: bool = True) -> dict:
    data = {
        "id": str(c.id),
        "name": c.name,
        "phone": c.phone,
        "phone_display": c.phone_display,
        "email": c.email,
        "language_preference": c.language_preference,
        "total_appointments": c.total_appointments,
        "total_conversations": c.total_conversations,
        "tags": c.tags,
        "last_seen_at": c.last_seen_at.isoformat() if c.last_seen_at else None,
        "last_summary_at": c.last_summary_at.isoformat() if c.last_summary_at else None,
        "created_at": c.created_at.isoformat(),
    }
    if with_memory:
        data["memory_summary"] = c.memory_summary
        data["preferences"] = c.preferences.model_dump()
    return data


@router.get("/")
async def list_customers(current: Business = Depends(get_current_user)):
    customers = await Customer.find(Customer.business_id == str(current.id)).to_list()
    customers.sort(
        key=lambda c: (c.last_seen_at or c.created_at),
        reverse=True,
    )
    return {"customers": [_serialize(c, with_memory=False) for c in customers]}


@router.get("/by-phone/{phone}")
async def get_by_phone(phone: str, current: Business = Depends(get_current_user)):
    customer = await customer_service.find_by_phone(str(current.id), phone)
    if not customer:
        # Not a 404 — the customers page calls this for every row; return None.
        return {"customer": None}
    # Attach recent appointments for convenience
    appts = (
        await Appointment.find(
            Appointment.business_id == str(current.id),
            Appointment.customer_phone == (customer.phone_display or phone),
        )
        .sort("-start_time")
        .to_list()
    )[:5]
    return {
        "customer": _serialize(customer),
        "recent_appointments": [
            {
                "id": str(a.id),
                "service_name": a.service_name,
                "start_time": a.start_time.isoformat(),
                "status": a.status,
            }
            for a in appts
        ],
    }


class UpdateCustomerRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    language_preference: Optional[str] = None
    tags: Optional[List[str]] = None
    memory_summary: Optional[str] = None
    preferences: Optional[CustomerPreferences] = None


@router.patch("/{customer_id}")
async def update_customer(
    customer_id: str,
    req: UpdateCustomerRequest,
    current: Business = Depends(get_current_user),
):
    customer = await Customer.get(customer_id)
    if not customer or customer.business_id != str(current.id):
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    if req.name is not None:
        customer.name = req.name
    if req.email is not None:
        customer.email = req.email or None
    if req.language_preference is not None:
        customer.language_preference = req.language_preference
    if req.tags is not None:
        customer.tags = [t.strip() for t in req.tags if t.strip()][:20]
    if req.memory_summary is not None:
        customer.memory_summary = req.memory_summary.strip() or None
    if req.preferences is not None:
        customer.preferences = req.preferences

    from datetime import datetime
    customer.updated_at = datetime.utcnow()
    await customer.save()
    return _serialize(customer)


@router.delete("/{customer_id}/memory")
async def reset_memory(customer_id: str, current: Business = Depends(get_current_user)):
    """Wipe just the AI memory (summary + tags + prefs) but keep the record."""
    customer = await Customer.get(customer_id)
    if not customer or customer.business_id != str(current.id):
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")
    customer.memory_summary = None
    customer.preferences = CustomerPreferences()
    customer.tags = []
    customer.last_summary_at = None
    await customer.save()
    return {"ok": True}
