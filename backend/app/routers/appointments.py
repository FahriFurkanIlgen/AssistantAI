"""
Appointments Router - CRUD for appointments dashboard.
Business owners see all appointments (filterable by staff).
Staff members see only their own appointments.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.business import Business
from app.models.appointment import Appointment
from app.core.auth import get_current_user, get_current_business, get_current_actor, ActorContext
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("/")
async def list_appointments(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    staff_id: Optional[str] = Query(None, description="Filter by staff member (business owner only)"),
    actor: ActorContext = Depends(get_current_actor),
):
    service = AppointmentService(actor.business)

    # Staff can only see their own appointments; business owner can filter by staff
    effective_staff_id = actor.staff_id if actor.actor_type == "staff" else staff_id
    appointments = await service.get_appointments(
        start=start, end=end, status=status, staff_id=effective_staff_id
    )
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
            "staff_id": a.staff_id,
            "staff_name": a.staff_name,
            "google_event_id": a.google_event_id,
            "created_at": a.created_at.isoformat(),
        }
        for a in appointments
    ]


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    actor: ActorContext = Depends(get_current_actor),
):
    appt = await Appointment.get(appointment_id)
    if not appt or appt.business_id != actor.business_id:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")

    # Staff members can only cancel their own appointments
    if actor.actor_type == "staff" and appt.staff_id != actor.staff_id:
        raise HTTPException(status_code=403, detail="Bu randevuyu iptal etme yetkiniz yok")

    service = AppointmentService(actor.business)
    success = await service.cancel_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    return {"message": "Randevu iptal edildi"}


@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    body: dict,
    actor: ActorContext = Depends(get_current_actor),
):
    """Update appointment status (confirm/complete/cancel)."""
    new_status = body.get("status")
    allowed = {"confirmed", "pending", "cancelled", "completed"}
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Geçersiz durum. İzin verilenler: {allowed}")

    appt = await Appointment.get(appointment_id)
    if not appt or appt.business_id != actor.business_id:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")

    # Staff members can only update their own appointments
    if actor.actor_type == "staff" and appt.staff_id != actor.staff_id:
        raise HTTPException(status_code=403, detail="Bu randevuyu güncelleme yetkiniz yok")

    appt.status = new_status
    appt.updated_at = datetime.utcnow()
    await appt.save()
    return {"message": "Durum güncellendi", "status": new_status}


@router.get("/stats")
async def get_stats(current_business: Business = Depends(get_current_business)):
    """Return analytics stats for the dashboard (business owner only)."""
    business_id = str(current_business.id)
    all_appts = await Appointment.find({"business_id": business_id}).to_list()

    now = datetime.utcnow()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    this_month = [a for a in all_appts if a.start_time >= this_month_start]
    last_month = [a for a in all_appts if last_month_start <= a.start_time < this_month_start]

    confirmed_this = [a for a in this_month if a.status in ("confirmed", "completed")]
    cancelled_this = [a for a in this_month if a.status == "cancelled"]

    # Monthly trend (last 6 months)
    monthly: dict = defaultdict(int)
    for a in all_appts:
        if a.status in ("confirmed", "completed"):
            key = a.start_time.strftime("%Y-%m")
            monthly[key] += 1

    months_sorted = sorted(monthly.keys())[-6:]
    monthly_trend = [{"month": m, "count": monthly[m]} for m in months_sorted]

    # Top services
    service_counts: dict = defaultdict(int)
    for a in all_appts:
        if a.status in ("confirmed", "completed"):
            service_counts[a.service_name] += 1
    top_services = sorted(
        [{"name": k, "count": v} for k, v in service_counts.items()],
        key=lambda x: -x["count"]
    )[:5]

    # Per-staff appointment counts
    staff_counts: dict = defaultdict(lambda: {"name": "Atanmamış", "count": 0})
    for a in all_appts:
        if a.status in ("confirmed", "completed"):
            key = a.staff_id or "unassigned"
            staff_counts[key]["count"] += 1
            if a.staff_name:
                staff_counts[key]["name"] = a.staff_name
    staff_breakdown = [
        {"staff_id": k, "staff_name": v["name"], "count": v["count"]}
        for k, v in staff_counts.items()
    ]

    # Upcoming (next 7 days)
    week_end = now + timedelta(days=7)
    upcoming = [
        a for a in all_appts
        if now <= a.start_time <= week_end and a.status in ("confirmed", "pending")
    ]

    cancel_rate = (
        round(len(cancelled_this) / len(this_month) * 100) if this_month else 0
    )

    return {
        "total_all_time": len([a for a in all_appts if a.status in ("confirmed", "completed")]),
        "this_month": len(confirmed_this),
        "last_month": len([a for a in last_month if a.status in ("confirmed", "completed")]),
        "cancelled_this_month": len(cancelled_this),
        "cancel_rate_percent": cancel_rate,
        "upcoming_7_days": len(upcoming),
        "monthly_trend": monthly_trend,
        "top_services": top_services,
        "staff_breakdown": staff_breakdown,
    }
