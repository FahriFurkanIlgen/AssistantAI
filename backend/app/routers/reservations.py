"""
Reservations Router — CRUD for restaurant reservations (dashboard + public).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from beanie.operators import In
from typing import Optional, List
from datetime import datetime

from app.models.reservation import Reservation
from app.models.business import Business
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


class CreateReservationRequest(BaseModel):
    table_id: Optional[str] = None       # single-table (required if table_ids empty)
    table_ids: List[str] = []            # multi-table combo (overrides table_id)
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    party_size: int = 2
    date: str           # YYYY-MM-DD
    shift_name: str
    shift_start: str
    shift_end: str
    special_requests: Optional[str] = None
    notes: Optional[str] = None

    @property
    def all_table_ids(self) -> List[str]:
        """Returns the canonical list of table IDs for this reservation."""
        return self.table_ids if self.table_ids else ([self.table_id] if self.table_id else [])


def _get_reserved_ids(reservations: list) -> set:
    """Collect all occupied table IDs from existing reservations (single + combo)."""
    ids: set = set()
    for r in reservations:
        if r.table_ids:
            ids.update(r.table_ids)
        else:
            ids.add(r.table_id)
    return ids


def _find_combinations(free_tables: list, party_size: int, section: Optional[str] = None, limit: int = 8) -> list:
    """
    Find pairs (and triplets if needed) of free tables whose combined
    capacity covers party_size. Returns best-fit results sorted by waste.
    """
    pool = [t for t in free_tables if not section or t.section == section]
    results = []

    # 2-table combos
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            cap = pool[i].capacity + pool[j].capacity
            if cap >= party_size:
                results.append({
                    "tables": [pool[i], pool[j]],
                    "combined_capacity": cap,
                    "waste": cap - party_size,
                })

    # 3-table combos only if no 2-table solution found
    if not results:
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                for k in range(j + 1, len(pool)):
                    cap = pool[i].capacity + pool[j].capacity + pool[k].capacity
                    if cap >= party_size:
                        results.append({
                            "tables": [pool[i], pool[j], pool[k]],
                            "combined_capacity": cap,
                            "waste": cap - party_size,
                        })

    results.sort(key=lambda x: x["waste"])
    return results[:limit]


class UpdateReservationRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    special_requests: Optional[str] = None
    table_id: Optional[str] = None
    table_number: Optional[str] = None
    table_section: Optional[str] = None


@router.get("")
async def list_reservations(
    date: Optional[str] = Query(None),
    shift_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_business: Business = Depends(get_current_user),
):
    """List reservations, optionally filtered by date / shift / status."""
    query = Reservation.find(Reservation.business_id == str(current_business.id))
    if date:
        query = query.find(Reservation.date == date)
    if shift_name:
        query = query.find(Reservation.shift_name == shift_name)
    if status:
        query = query.find(Reservation.status == status)

    reservations = await query.sort("date").to_list()
    return [_serialize(r) for r in reservations]


@router.post("")
async def create_reservation(
    req: CreateReservationRequest,
    current_business: Business = Depends(get_current_user),
):
    """Manually create a reservation from the dashboard."""
    cfg = current_business.restaurant
    if not cfg or not cfg.enabled:
        raise HTTPException(status_code=400, detail="Rezervasyon sistemi aktif değil.")

    all_ids = req.all_table_ids
    if not all_ids:
        raise HTTPException(status_code=400, detail="Masa seçilmedi.")

    tables = [next((t for t in cfg.tables if t.id == tid), None) for tid in all_ids]
    if any(t is None for t in tables):
        raise HTTPException(status_code=404, detail="Masa bulunamadı.")

    # Conflict check for every table in combo
    existing = await Reservation.find(
        Reservation.business_id == str(current_business.id),
        Reservation.date == req.date,
        Reservation.shift_name == req.shift_name,
        In(Reservation.status, ["confirmed", "seated"]),
    ).to_list()
    occupied = _get_reserved_ids(existing)
    clashing = [t for t in tables if t.id in occupied]
    if clashing:
        nums = ", ".join(f"Masa {t.number}" for t in clashing)
        raise HTTPException(status_code=409, detail=f"{nums} bu vardiyada zaten rezerve.")

    is_combo = len(tables) > 1
    primary = tables[0]
    now = datetime.utcnow()
    reservation = Reservation(
        business_id=str(current_business.id),
        table_id=primary.id,
        table_number=" + ".join(t.number for t in tables) if is_combo else primary.number,
        table_section=primary.section,
        table_ids=all_ids if is_combo else [],
        combined_capacity=sum(t.capacity for t in tables) if is_combo else None,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_email=req.customer_email,
        party_size=req.party_size,
        date=req.date,
        shift_name=req.shift_name,
        shift_start=req.shift_start,
        shift_end=req.shift_end,
        special_requests=req.special_requests,
        notes=req.notes,
        status="confirmed",
        channel="manual",
        created_at=now,
        updated_at=now,
    )
    await reservation.insert()
    return _serialize(reservation)


@router.patch("/{reservation_id}")
async def update_reservation(
    reservation_id: str,
    req: UpdateReservationRequest,
    current_business: Business = Depends(get_current_user),
):
    reservation = await Reservation.get(reservation_id)
    if not reservation or reservation.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")

    valid_statuses = {"confirmed", "seated", "completed", "cancelled", "no_show"}
    if req.status and req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Geçersiz durum: {req.status}")

    if req.status:
        reservation.status = req.status
    if req.notes is not None:
        reservation.notes = req.notes
    if req.special_requests is not None:
        reservation.special_requests = req.special_requests
    if req.table_id:
        cfg = current_business.restaurant
        table = next((t for t in cfg.tables if t.id == req.table_id), None)
        if table:
            reservation.table_id = req.table_id
            reservation.table_number = table.number
            reservation.table_section = table.section
    reservation.updated_at = datetime.utcnow()
    await reservation.save()
    return _serialize(reservation)


@router.delete("/{reservation_id}")
async def delete_reservation(
    reservation_id: str,
    current_business: Business = Depends(get_current_user),
):
    reservation = await Reservation.get(reservation_id)
    if not reservation or reservation.business_id != str(current_business.id):
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
    await reservation.delete()
    return {"ok": True}


@router.get("/stats/summary")
async def reservation_stats(
    date: Optional[str] = Query(None),
    current_business: Business = Depends(get_current_user),
):
    """Quick stats for dashboard overview."""
    base = Reservation.find(Reservation.business_id == str(current_business.id))
    if date:
        base = base.find(Reservation.date == date)
    all_res = await base.to_list()
    return {
        "total": len(all_res),
        "confirmed": sum(1 for r in all_res if r.status == "confirmed"),
        "seated": sum(1 for r in all_res if r.status == "seated"),
        "completed": sum(1 for r in all_res if r.status == "completed"),
        "cancelled": sum(1 for r in all_res if r.status == "cancelled"),
        "no_show": sum(1 for r in all_res if r.status == "no_show"),
        "total_covers": sum(r.party_size for r in all_res if r.status not in ("cancelled", "no_show")),
    }


# ─────────────────────────────────────────────────────────────
# PUBLIC endpoints (no auth — customer-facing)
# ─────────────────────────────────────────────────────────────

@router.get("/public/{slug}/config")
async def public_restaurant_config(slug: str):
    """Return reservation-relevant config for the public booking form."""
    business = await Business.find_one(Business.slug == slug)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı.")
    cfg = business.restaurant
    if not cfg or not cfg.enabled:
        raise HTTPException(status_code=404, detail="Bu işletmede rezervasyon aktif değil.")

    active_shifts = [
        {"id": s.id, "name": s.name, "start_time": s.start_time, "end_time": s.end_time, "days": s.days}
        for s in cfg.shifts if s.is_active
    ]
    sections = list({t.section for t in cfg.tables if t.is_active})
    return {
        "business_name": business.name,
        "logo_url": business.logo_url,
        "phone": business.phone,
        "address": business.address,
        "shifts": active_shifts,
        "sections": sections,
        "max_party_size": cfg.max_party_size,
        "reservation_window_days": cfg.reservation_window_days,
    }


@router.get("/public/{slug}/availability")
async def public_availability(
    slug: str,
    date: str = Query(...),
    shift_name: str = Query(...),
    party_size: int = Query(2),
    section: Optional[str] = Query(None),
):
    """Return available tables for a given date+shift+party_size."""
    business = await Business.find_one(Business.slug == slug)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı.")
    cfg = business.restaurant
    if not cfg or not cfg.enabled:
        raise HTTPException(status_code=404, detail="Rezervasyon aktif değil.")

    shift = next((s for s in cfg.shifts if s.name == shift_name and s.is_active), None)
    if not shift:
        raise HTTPException(status_code=404, detail="Vardiya bulunamadı.")

    # Reserved table IDs for this slot
    reserved = await Reservation.find(
        Reservation.business_id == str(business.id),
        Reservation.date == date,
        Reservation.shift_name == shift_name,
        In(Reservation.status, ["confirmed", "seated"]),
    ).to_list()
    reserved_ids = _get_reserved_ids(reserved)

    # All free tables (ignore section filter for combos)
    all_free = [
        t for t in cfg.tables
        if t.is_active and t.id not in reserved_ids
    ]

    # Single tables that fit
    available = [
        t for t in all_free
        if t.capacity >= party_size
        and (not section or t.section == section)
    ]
    available.sort(key=lambda t: t.capacity)

    # Combinations (only when single tables are scarce or none fit)
    combos = _find_combinations(all_free, party_size, section=section if section else None)

    def fmt_table(t):
        return {"id": t.id, "number": t.number, "capacity": t.capacity,
                "section": t.section, "shape": t.shape}

    return {
        "shift_start": shift.start_time,
        "shift_end": shift.end_time,
        "available_tables": [fmt_table(t) for t in available],
        "combinations": [
            {
                "tables": [fmt_table(t) for t in c["tables"]],
                "combined_capacity": c["combined_capacity"],
                "table_ids": [t.id for t in c["tables"]],
                "label": " + ".join(f"Masa {t.number}" for t in c["tables"]),
            }
            for c in combos
        ],
    }


@router.post("/public/{slug}")
async def public_create_reservation(slug: str, req: CreateReservationRequest):
    """Create a reservation from the public booking form (no auth)."""
    business = await Business.find_one(Business.slug == slug)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı.")
    cfg = business.restaurant
    if not cfg or not cfg.enabled:
        raise HTTPException(status_code=400, detail="Rezervasyon sistemi aktif değil.")

    all_ids = req.all_table_ids
    if not all_ids:
        raise HTTPException(status_code=400, detail="Masa seçilmedi.")

    tables = [next((t for t in cfg.tables if t.id == tid), None) for tid in all_ids]
    if any(t is None for t in tables):
        raise HTTPException(status_code=404, detail="Masa bulunamadı.")

    # Check conflict for every table in the combo
    existing = await Reservation.find(
        Reservation.business_id == str(business.id),
        Reservation.date == req.date,
        Reservation.shift_name == req.shift_name,
        In(Reservation.status, ["confirmed", "seated"]),
    ).to_list()
    occupied = _get_reserved_ids(existing)
    clashing = [t for t in tables if t.id in occupied]
    if clashing:
        nums = ", ".join(f"Masa {t.number}" for t in clashing)
        raise HTTPException(status_code=409, detail=f"{nums} bu vardiyada dolu.")

    is_combo = len(tables) > 1
    primary = tables[0]
    now = datetime.utcnow()
    reservation = Reservation(
        business_id=str(business.id),
        table_id=primary.id,
        table_number=" + ".join(t.number for t in tables) if is_combo else primary.number,
        table_section=primary.section,
        table_ids=all_ids if is_combo else [],
        combined_capacity=sum(t.capacity for t in tables) if is_combo else None,
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_email=req.customer_email,
        party_size=req.party_size,
        date=req.date,
        shift_name=req.shift_name,
        shift_start=req.shift_start,
        shift_end=req.shift_end,
        special_requests=req.special_requests,
        status="confirmed",
        channel="web",
        created_at=now,
        updated_at=now,
    )
    await reservation.insert()
    return _serialize(reservation)


def _serialize(r: Reservation) -> dict:
    return {
        "id": str(r.id),
        "business_id": r.business_id,
        "table_id": r.table_id,
        "table_ids": r.table_ids or [],
        "table_number": r.table_number,
        "table_section": r.table_section,
        "combined_capacity": r.combined_capacity,
        "customer_name": r.customer_name,
        "customer_phone": r.customer_phone,
        "customer_email": r.customer_email,
        "party_size": r.party_size,
        "date": r.date,
        "shift_name": r.shift_name,
        "shift_start": r.shift_start,
        "shift_end": r.shift_end,
        "special_requests": r.special_requests,
        "notes": r.notes,
        "status": r.status,
        "channel": r.channel,
        "created_at": r.created_at.isoformat(),
    }
