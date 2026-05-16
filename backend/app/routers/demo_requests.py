"""
Demo Request Router — public endpoint for potential customers.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.models.demo_request import DemoRequest

router = APIRouter(prefix="/api/demo-request", tags=["demo-request"])


class DemoRequestCreate(BaseModel):
    name: str
    business_name: str
    sector: str = "general"
    phone: str
    email: EmailStr
    city: Optional[str] = None
    message: Optional[str] = None


@router.post("", status_code=201)
async def create_demo_request(req: DemoRequestCreate):
    # prevent duplicate e-mail submissions
    existing = await DemoRequest.find_one(DemoRequest.email == req.email)
    if existing:
        # idempotent: update rather than error
        existing.name = req.name
        existing.business_name = req.business_name
        existing.sector = req.sector
        existing.phone = req.phone
        existing.city = req.city
        existing.message = req.message
        existing.updated_at = datetime.utcnow()
        await existing.save()
        return {"ok": True, "id": str(existing.id)}

    dr = DemoRequest(
        name=req.name,
        business_name=req.business_name,
        sector=req.sector,
        phone=req.phone,
        email=req.email,
        city=req.city,
        message=req.message,
    )
    await dr.insert()
    return {"ok": True, "id": str(dr.id)}
