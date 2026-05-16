"""
Admin Router — protected by ADMIN_SECRET_KEY header.
Provides full control: demo requests, business accounts, impersonation.
"""
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.config import settings
from app.models.demo_request import DemoRequest
from app.models.business import Business
from app.core.security import hash_password
from app.core.auth import create_access_token

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Auth guard ────────────────────────────────────────────────────────────────

def require_admin(x_admin_key: str = Header(..., alias="x-admin-key")):
    if not settings.ADMIN_SECRET_KEY or x_admin_key != settings.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim")


# ── Demo Requests ─────────────────────────────────────────────────────────────

@router.get("/demo-requests")
async def list_demo_requests(x_admin_key: str = Header(..., alias="x-admin-key")):
    require_admin(x_admin_key)
    requests = await DemoRequest.find_all().sort("-created_at").to_list()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "business_name": r.business_name,
            "sector": r.sector,
            "phone": r.phone,
            "email": r.email,
            "city": r.city,
            "message": r.message,
            "status": r.status,
            "notes": r.notes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in requests
    ]


class UpdateDemoRequest(BaseModel):
    status: Optional[str] = None     # pending | contacted | converted | rejected
    notes: Optional[str] = None


@router.patch("/demo-requests/{request_id}")
async def update_demo_request(
    request_id: str,
    body: UpdateDemoRequest,
    x_admin_key: str = Header(..., alias="x-admin-key"),
):
    require_admin(x_admin_key)
    dr = await DemoRequest.get(request_id)
    if not dr:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")
    if body.status is not None:
        dr.status = body.status
    if body.notes is not None:
        dr.notes = body.notes
    dr.updated_at = datetime.utcnow()
    await dr.save()
    return {"ok": True}


@router.delete("/demo-requests/{request_id}")
async def delete_demo_request(
    request_id: str,
    x_admin_key: str = Header(..., alias="x-admin-key"),
):
    require_admin(x_admin_key)
    dr = await DemoRequest.get(request_id)
    if not dr:
        raise HTTPException(status_code=404, detail="Talep bulunamadı")
    await dr.delete()
    return {"ok": True}


# ── Businesses ────────────────────────────────────────────────────────────────

@router.get("/businesses")
async def list_businesses(x_admin_key: str = Header(..., alias="x-admin-key")):
    require_admin(x_admin_key)
    businesses = await Business.find_all().sort("-created_at").to_list()
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "slug": b.slug,
            "email": b.email,
            "sector": b.sector,
            "city": b.city,
            "phone": b.phone,
            "is_active": b.is_active,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in businesses
    ]


class AdminCreateBusiness(BaseModel):
    name: str
    slug: str
    email: EmailStr
    password: str
    sector: str = "general"
    phone: Optional[str] = None
    city: Optional[str] = None


@router.post("/businesses", status_code=201)
async def admin_create_business(
    body: AdminCreateBusiness,
    x_admin_key: str = Header(..., alias="x-admin-key"),
):
    require_admin(x_admin_key)
    if await Business.find_one(Business.email == body.email):
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı")
    if await Business.find_one(Business.slug == body.slug):
        raise HTTPException(status_code=400, detail="Bu slug zaten kullanımda")

    now = datetime.utcnow()
    biz = Business(
        name=body.name,
        slug=body.slug.lower().strip(),
        email=body.email,
        hashed_password=hash_password(body.password),
        sector=body.sector,
        phone=body.phone,
        city=body.city,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    await biz.insert()
    return {"ok": True, "id": str(biz.id), "slug": biz.slug}


class AdminUpdateBusiness(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    sector: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None


@router.patch("/businesses/{business_id}")
async def admin_update_business(
    business_id: str,
    body: AdminUpdateBusiness,
    x_admin_key: str = Header(..., alias="x-admin-key"),
):
    require_admin(x_admin_key)
    biz = await Business.get(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    if body.name is not None:
        biz.name = body.name
    if body.email is not None:
        biz.email = body.email
    if body.password is not None:
        biz.hashed_password = hash_password(body.password)
    if body.sector is not None:
        biz.sector = body.sector
    if body.phone is not None:
        biz.phone = body.phone
    if body.city is not None:
        biz.city = body.city
    if body.is_active is not None:
        biz.is_active = body.is_active
    biz.updated_at = datetime.utcnow()
    await biz.save()
    return {"ok": True}


@router.post("/businesses/{business_id}/impersonate")
async def impersonate_business(
    business_id: str,
    x_admin_key: str = Header(..., alias="x-admin-key"),
):
    """Return a valid JWT for the given business so admin can log in as them."""
    require_admin(x_admin_key)
    biz = await Business.get(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    token = create_access_token({"sub": str(biz.id), "type": "business"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "business_id": str(biz.id),
        "business_name": biz.name,
        "slug": biz.slug,
    }
