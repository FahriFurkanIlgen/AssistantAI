"""
Appointments Router - CRUD for appointments dashboard.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.business import Business
from app.models.appointment import Appointment
from app.core.auth import get_current_user
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("/")
async def list_appointments(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    current_business: Business = Depends(get_current_user),
):
    service = AppointmentService(current_business)
    appointments = await service.get_appointments(start=start, end=end, status=status)
    return [
        {
            "id": str(a.id),
            "customer_name": a.customer_name,
            "customer_phone": a.customer_phone,
            "customer_email": a.customer_email,
            "service_name": a.service_name,
            "notes": a.notes,
            "start_time": a.start_time.isoformat(),
            "end_time": a.end_time.isoformat(),
            "duration_minutes": a.duration_minutes,
            "status": a.status,
            "google_event_id": a.google_event_id,
            "created_at": a.created_at.isoformat(),
        }
        for a in appointments
    ]


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    current_business: Business = Depends(get_current_user),
):
    service = AppointmentService(current_business)
    success = await service.cancel_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    return {"message": "Randevu iptal edildi"}
