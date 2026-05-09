"""
Staff Router - CRUD for staff members + per-staff Google Calendar.
"""
import secrets
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.models.business import Business, WorkingSchedule
from app.models.staff_member import StaffMember
from app.models.appointment import Appointment
from app.core.auth import get_current_business, get_current_actor, ActorContext
from app.core.security import hash_password
from app.services.calendar_service import get_authorization_url, exchange_code_for_tokens
from app.config import settings

router = APIRouter(prefix="/api/staff", tags=["staff"])

# Temporary in-memory state store for OAuth (use Redis in production)
_staff_oauth_states: dict = {}


# ── Request / Response schemas ───────────────────────────────────────────────

class CreateStaffRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    service_names: List[str] = []
    working_schedule: Optional[WorkingSchedule] = None


class UpdateStaffRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    service_names: Optional[List[str]] = None
    is_active: Optional[bool] = None


# ── Helper ───────────────────────────────────────────────────────────────────

def _staff_response(s: StaffMember) -> dict:
    return {
        "id": str(s.id),
        "name": s.name,
        "email": s.email,
        "phone": s.phone,
        "bio": s.bio,
        "service_names": s.service_names,
        "working_schedule": s.working_schedule.model_dump(),
        "google_connected": s.google_refresh_token is not None,
        "is_active": s.is_active,
        "created_at": s.created_at.isoformat(),
    }


# ── Staff CRUD endpoints ─────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_staff(
    req: CreateStaffRequest,
    current_business: Business = Depends(get_current_business),
):
    """Business owner creates a new staff member."""
    # Unique email check within the business
    existing = await StaffMember.find_one(
        StaffMember.email == req.email,
        StaffMember.business_id == str(current_business.id),
    )
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı")

    staff = StaffMember(
        business_id=str(current_business.id),
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
        phone=req.phone,
        bio=req.bio,
        service_names=req.service_names,
        working_schedule=req.working_schedule or WorkingSchedule(),
    )
    await staff.insert()
    return _staff_response(staff)


@router.get("/")
async def list_staff(current_business: Business = Depends(get_current_business)):
    """List all staff members for the business."""
    members = await StaffMember.find(
        StaffMember.business_id == str(current_business.id)
    ).to_list()
    return [_staff_response(s) for s in members]


@router.get("/{staff_id}")
async def get_staff(
    staff_id: str,
    actor: ActorContext = Depends(get_current_actor),
):
    """Get a staff member profile. Accessible by business owner or the staff member themselves."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != actor.business_id:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    # Staff members can only view their own profile
    if actor.actor_type == "staff" and actor.staff_id != staff_id:
        raise HTTPException(status_code=403, detail="Yetersiz yetki")

    return _staff_response(staff)


@router.patch("/{staff_id}")
async def update_staff(
    staff_id: str,
    req: UpdateStaffRequest,
    current_business: Business = Depends(get_current_business),
):
    """Update a staff member (business owner only)."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    update_data = req.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(staff, key, value)
    staff.updated_at = datetime.utcnow()
    await staff.save()
    return _staff_response(staff)


@router.delete("/{staff_id}")
async def deactivate_staff(
    staff_id: str,
    current_business: Business = Depends(get_current_business),
):
    """Deactivate a staff member (soft delete). Business owner only."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    staff.is_active = False
    staff.updated_at = datetime.utcnow()
    await staff.save()
    return {"message": "Personel deaktif edildi"}


# ── Working schedule endpoints ───────────────────────────────────────────────

@router.get("/{staff_id}/schedule")
async def get_staff_schedule(
    staff_id: str,
    actor: ActorContext = Depends(get_current_actor),
):
    """Get working schedule of a staff member."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != actor.business_id:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    if actor.actor_type == "staff" and actor.staff_id != staff_id:
        raise HTTPException(status_code=403, detail="Yetersiz yetki")

    return staff.working_schedule.model_dump()


@router.patch("/{staff_id}/schedule")
async def update_staff_schedule(
    staff_id: str,
    schedule: WorkingSchedule,
    current_business: Business = Depends(get_current_business),
):
    """Update working schedule of a staff member (business owner only)."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    staff.working_schedule = schedule
    staff.updated_at = datetime.utcnow()
    await staff.save()
    return {"message": "Takvim güncellendi", "schedule": schedule.model_dump()}


# ── Staff appointments summary ────────────────────────────────────────────────

@router.get("/{staff_id}/appointments")
async def get_staff_appointments(
    staff_id: str,
    actor: ActorContext = Depends(get_current_actor),
):
    """List appointments assigned to a specific staff member."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != actor.business_id:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    if actor.actor_type == "staff" and actor.staff_id != staff_id:
        raise HTTPException(status_code=403, detail="Yetersiz yetki")

    appointments = await Appointment.find(
        {"business_id": actor.business_id, "staff_id": staff_id}
    ).sort("start_time").to_list()

    return [
        {
            "id": str(a.id),
            "customer_name": a.customer_name,
            "customer_phone": a.customer_phone,
            "service_name": a.service_name,
            "start_time": a.start_time.isoformat(),
            "end_time": a.end_time.isoformat(),
            "status": a.status,
        }
        for a in appointments
    ]


# ── Per-staff Google Calendar OAuth ─────────────────────────────────────────

@router.get("/{staff_id}/calendar/connect")
async def connect_staff_google(
    staff_id: str,
    current_business: Business = Depends(get_current_business),
):
    """Initiate Google OAuth2 flow for a staff member."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    state = secrets.token_urlsafe(32)
    _staff_oauth_states[state] = {"staff_id": staff_id, "business_id": str(current_business.id)}

    auth_url = get_authorization_url(state=state)
    return {"auth_url": auth_url}


@router.get("/calendar/oauth/callback")
async def staff_oauth_callback(code: str, state: str):
    """Handle Google OAuth2 callback for a staff member."""
    state_data = _staff_oauth_states.pop(state, None)
    if not state_data:
        raise HTTPException(status_code=400, detail="Geçersiz OAuth state")

    staff = await StaffMember.get(state_data["staff_id"])
    if not staff:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    try:
        tokens = exchange_code_for_tokens(code)
        staff.google_access_token = tokens["access_token"]
        staff.google_refresh_token = tokens["refresh_token"]
        if tokens.get("expiry"):
            staff.google_token_expiry = datetime.fromisoformat(tokens["expiry"])
        staff.updated_at = datetime.utcnow()
        await staff.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token alınamadı: {str(e)}")

    frontend_url = settings.ALLOWED_ORIGINS[0]
    return RedirectResponse(url=f"{frontend_url}/dashboard/staff?google=connected")


@router.delete("/{staff_id}/calendar")
async def disconnect_staff_google(
    staff_id: str,
    current_business: Business = Depends(get_current_business),
):
    """Remove Google Calendar connection for a staff member."""
    staff = await StaffMember.get(staff_id)
    if not staff or staff.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Personel bulunamadı")

    staff.google_access_token = None
    staff.google_refresh_token = None
    staff.google_token_expiry = None
    staff.updated_at = datetime.utcnow()
    await staff.save()
    return {"message": "Google Calendar bağlantısı kaldırıldı"}
