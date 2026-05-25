"""
Tables Router — masa ve vardiya yönetimi (dashboard).
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.business import Business, RestaurantTable, DiningShift, RestaurantConfig
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/tables", tags=["tables"])


# ── Request schemas ──────────────────────────────────────────────────────────

class TableRequest(BaseModel):
    number: str
    name: Optional[str] = None
    capacity: int = 4
    section: str = "iç"
    shape: str = "square"
    is_active: bool = True
    x: float = 10.0
    y: float = 10.0
    width: float = 8.0
    height: float = 8.0


class TableLayoutItem(BaseModel):
    id: str
    x: float
    y: float
    width: float
    height: float


class ShiftRequest(BaseModel):
    name: str
    start_time: str
    end_time: str
    is_active: bool = True
    days: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class RestaurantSettingsRequest(BaseModel):
    enabled: Optional[bool] = None
    reservation_duration: Optional[int] = None
    max_party_size: Optional[int] = None
    reservation_window_days: Optional[int] = None


# ── Restaurant settings ──────────────────────────────────────────────────────

@router.get("/restaurant-config")
async def get_restaurant_config(current_business: Business = Depends(get_current_user)):
    cfg = current_business.restaurant
    return {
        "enabled": cfg.enabled,
        "reservation_duration": cfg.reservation_duration,
        "max_party_size": cfg.max_party_size,
        "reservation_window_days": cfg.reservation_window_days,
        "tables": [_serialize_table(t) for t in cfg.tables],
        "shifts": [_serialize_shift(s) for s in cfg.shifts],
    }


@router.patch("/restaurant-config")
async def update_restaurant_settings(
    req: RestaurantSettingsRequest,
    current_business: Business = Depends(get_current_user),
):
    cfg = current_business.restaurant
    if req.enabled is not None:
        cfg.enabled = req.enabled
    if req.reservation_duration is not None:
        cfg.reservation_duration = req.reservation_duration
    if req.max_party_size is not None:
        cfg.max_party_size = req.max_party_size
    if req.reservation_window_days is not None:
        cfg.reservation_window_days = req.reservation_window_days
    current_business.restaurant = cfg
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return {"ok": True}


# ── Tables ───────────────────────────────────────────────────────────────────

@router.get("")
async def list_tables(current_business: Business = Depends(get_current_user)):
    return [_serialize_table(t) for t in current_business.restaurant.tables]


@router.post("")
async def create_table(
    req: TableRequest,
    current_business: Business = Depends(get_current_user),
):
    table = RestaurantTable(
        id=str(uuid.uuid4()),
        number=req.number,
        name=req.name,
        capacity=req.capacity,
        section=req.section,
        shape=req.shape,
        is_active=req.is_active,
        x=req.x,
        y=req.y,
        width=req.width,
        height=req.height,
    )
    current_business.restaurant.tables.append(table)
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return _serialize_table(table)


@router.patch("/{table_id}")
async def update_table(
    table_id: str,
    req: TableRequest,
    current_business: Business = Depends(get_current_user),
):
    tables = current_business.restaurant.tables
    idx = next((i for i, t in enumerate(tables) if t.id == table_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Masa bulunamadı.")

    t = tables[idx]
    t.number = req.number
    t.name = req.name
    t.capacity = req.capacity
    t.section = req.section
    t.shape = req.shape
    t.is_active = req.is_active
    t.x = req.x
    t.y = req.y
    t.width = req.width
    t.height = req.height
    current_business.restaurant.tables[idx] = t
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return _serialize_table(t)


@router.delete("/{table_id}")
async def delete_table(
    table_id: str,
    current_business: Business = Depends(get_current_user),
):
    tables = current_business.restaurant.tables
    new_tables = [t for t in tables if t.id != table_id]
    if len(new_tables) == len(tables):
        raise HTTPException(status_code=404, detail="Masa bulunamadı.")
    current_business.restaurant.tables = new_tables
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return {"ok": True}


@router.post("/layout")
async def save_layout(
    items: List[TableLayoutItem],
    current_business: Business = Depends(get_current_user),
):
    """Bulk-update table positions from floor plan drag-and-drop."""
    pos_map = {item.id: item for item in items}
    for table in current_business.restaurant.tables:
        if table.id in pos_map:
            p = pos_map[table.id]
            table.x = p.x
            table.y = p.y
            table.width = p.width
            table.height = p.height
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return {"ok": True}


# ── Shifts ───────────────────────────────────────────────────────────────────

@router.get("/shifts")
async def list_shifts(current_business: Business = Depends(get_current_user)):
    return [_serialize_shift(s) for s in current_business.restaurant.shifts]


@router.post("/shifts")
async def create_shift(
    req: ShiftRequest,
    current_business: Business = Depends(get_current_user),
):
    shift = DiningShift(
        id=str(uuid.uuid4()),
        name=req.name,
        start_time=req.start_time,
        end_time=req.end_time,
        is_active=req.is_active,
        days=req.days,
    )
    current_business.restaurant.shifts.append(shift)
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return _serialize_shift(shift)


@router.patch("/shifts/{shift_id}")
async def update_shift(
    shift_id: str,
    req: ShiftRequest,
    current_business: Business = Depends(get_current_user),
):
    shifts = current_business.restaurant.shifts
    idx = next((i for i, s in enumerate(shifts) if s.id == shift_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Vardiya bulunamadı.")
    s = shifts[idx]
    s.name = req.name
    s.start_time = req.start_time
    s.end_time = req.end_time
    s.is_active = req.is_active
    s.days = req.days
    current_business.restaurant.shifts[idx] = s
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return _serialize_shift(s)


@router.delete("/shifts/{shift_id}")
async def delete_shift(
    shift_id: str,
    current_business: Business = Depends(get_current_user),
):
    shifts = current_business.restaurant.shifts
    new_shifts = [s for s in shifts if s.id != shift_id]
    if len(new_shifts) == len(shifts):
        raise HTTPException(status_code=404, detail="Vardiya bulunamadı.")
    current_business.restaurant.shifts = new_shifts
    current_business.updated_at = datetime.utcnow()
    await current_business.save()
    return {"ok": True}


# ── Serializers ──────────────────────────────────────────────────────────────

def _serialize_table(t: RestaurantTable) -> dict:
    return {
        "id": t.id,
        "number": t.number,
        "name": t.name,
        "capacity": t.capacity,
        "section": t.section,
        "shape": t.shape,
        "is_active": t.is_active,
        "x": t.x,
        "y": t.y,
        "width": t.width,
        "height": t.height,
    }


def _serialize_shift(s: DiningShift) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "start_time": s.start_time,
        "end_time": s.end_time,
        "is_active": s.is_active,
        "days": s.days,
    }
