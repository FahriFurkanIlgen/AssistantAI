"""
Reservation Service — otomatik masa atama ve rezervasyon yönetimi.

Otomatik masa seçim algoritması:
  1. İstenen tarihin ve vardiyasının mevcut rezervasyonlarını çek.
  2. O vardiyada zaten rezerve edilmiş masaları hariç tut.
  3. Kalan aktif masalar arasında kişi sayısına ≥ capacity olanları filtrele.
  4. En az kapasiteli (en uygun sıkışık değil) masayı seç — "best fit" mantığı.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.models.business import Business, RestaurantTable, DiningShift
from app.models.reservation import Reservation
from app.models.conversation import Conversation
from app.services import customer_service
from beanie.operators import In


class ReservationService:
    def __init__(self, business: Business):
        self.business = business
        self.cfg = business.restaurant

    # ── AI Tool Executor ────────────────────────────────────────────────────

    async def execute_tool(self, fn_name: str, fn_args: dict, conversation: Conversation) -> dict:
        if fn_name == "get_shifts":
            return self._get_shifts()
        elif fn_name == "check_table_availability":
            return await self._check_table_availability(
                date=fn_args.get("date", ""),
                shift_name=fn_args.get("shift_name", ""),
                party_size=fn_args.get("party_size", 2),
            )
        elif fn_name == "create_reservation":
            return await self._create_reservation(fn_args, conversation)
        elif fn_name == "cancel_reservation":
            return await self._cancel_reservation(fn_args, conversation)
        else:
            return {"error": f"Unknown tool: {fn_name}"}

    # ── Tool implementations ────────────────────────────────────────────────

    def _get_shifts(self) -> dict:
        """Return active dining shifts."""
        if not self.cfg or not self.cfg.enabled:
            return {"error": "Rezervasyon sistemi bu işletmede aktif değil."}
        active = [s for s in self.cfg.shifts if s.is_active]
        if not active:
            return {"shifts": [], "message": "Henüz vardiya tanımlanmamış."}
        return {
            "shifts": [
                {
                    "id": s.id,
                    "name": s.name,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "days": s.days,
                }
                for s in active
            ],
            "reservation_duration_minutes": self.cfg.reservation_duration,
            "max_party_size": self.cfg.max_party_size,
            "reservation_window_days": self.cfg.reservation_window_days,
        }

    async def _check_table_availability(
        self, date: str, shift_name: str, party_size: int
    ) -> dict:
        """Find available tables for given date + shift + party size."""
        if not self.cfg or not self.cfg.enabled:
            return {"error": "Rezervasyon sistemi bu işletmede aktif değil."}

        # Find requested shift
        shift = next((s for s in self.cfg.shifts if s.name.lower() == shift_name.lower() and s.is_active), None)
        if not shift:
            available_shifts = [s.name for s in self.cfg.shifts if s.is_active]
            return {
                "available": False,
                "message": f"'{shift_name}' adında bir vardiya bulunamadı.",
                "available_shifts": available_shifts,
            }

        # Validate party size
        if party_size > self.cfg.max_party_size:
            return {
                "available": False,
                "message": f"Maksimum kişi sayısı {self.cfg.max_party_size}. Lütfen işletmeyle iletişime geçin.",
            }

        # Get already reserved table IDs for this date+shift
        existing = await Reservation.find(
            Reservation.business_id == str(self.business.id),
            Reservation.date == date,
            Reservation.shift_name == shift.name,
            In(Reservation.status, ["confirmed", "seated"]),
        ).to_list()
        reserved_ids = set()
        for r in existing:
            reserved_ids.update(r.table_ids if r.table_ids else [r.table_id])

        # Find suitable tables
        candidates = [
            t for t in self.cfg.tables
            if t.is_active
            and t.id not in reserved_ids
            and t.capacity >= party_size
        ]

        if not candidates:
            return {
                "available": False,
                "message": f"{date} tarihinde {shift.name} vardiyasında {party_size} kişilik müsait masa bulunmuyor.",
                "date": date,
                "shift": shift.name,
            }

        # Best-fit: smallest capacity that still fits
        best = min(candidates, key=lambda t: t.capacity)

        return {
            "available": True,
            "date": date,
            "shift": shift.name,
            "shift_start": shift.start_time,
            "shift_end": shift.end_time,
            "table_number": best.number,
            "table_section": best.section,
            "table_capacity": best.capacity,
            "party_size": party_size,
            "message": (
                f"{date} tarihinde {shift.name} vardiyası ({shift.start_time}–{shift.end_time}) için "
                f"{best.section} bölümünde Masa {best.number} ({best.capacity} kişilik) müsait."
            ),
        }

    async def _create_reservation(self, args: dict, conversation: Conversation) -> dict:
        """Auto-assign best table and create reservation."""
        if not self.cfg or not self.cfg.enabled:
            return {"error": "Rezervasyon sistemi bu işletmede aktif değil."}

        date = args.get("date", "")
        shift_name = args.get("shift_name", "")
        party_size = int(args.get("party_size", 2))
        customer_name = args.get("customer_name", "")
        customer_phone = args.get("customer_phone", "")
        customer_email = args.get("customer_email")
        special_requests = args.get("special_requests")

        if not all([date, shift_name, customer_name, customer_phone]):
            return {"error": "date, shift_name, customer_name ve customer_phone zorunludur."}

        # Find shift
        shift = next((s for s in self.cfg.shifts if s.name.lower() == shift_name.lower() and s.is_active), None)
        if not shift:
            return {"error": f"'{shift_name}' vardiyası bulunamadı."}

        # Get reserved table IDs
        existing = await Reservation.find(
            Reservation.business_id == str(self.business.id),
            Reservation.date == date,
            Reservation.shift_name == shift.name,
            In(Reservation.status, ["confirmed", "seated"]),
        ).to_list()
        reserved_ids = set()
        for r in existing:
            reserved_ids.update(r.table_ids if r.table_ids else [r.table_id])

        # Best-fit table (single)
        candidates = [
            t for t in self.cfg.tables
            if t.is_active and t.id not in reserved_ids and t.capacity >= party_size
        ]
        if not candidates:
            # Try 2-table combination
            free = [t for t in self.cfg.tables if t.is_active and t.id not in reserved_ids]
            combo = None
            for i in range(len(free)):
                for j in range(i + 1, len(free)):
                    if free[i].capacity + free[j].capacity >= party_size:
                        if combo is None or (free[i].capacity + free[j].capacity) < (combo[0].capacity + combo[1].capacity):
                            combo = [free[i], free[j]]
            if combo:
                now = datetime.utcnow()
                reservation = Reservation(
                    business_id=str(self.business.id),
                    table_id=combo[0].id,
                    table_number=" + ".join(t.number for t in combo),
                    table_section=combo[0].section,
                    table_ids=[t.id for t in combo],
                    combined_capacity=sum(t.capacity for t in combo),
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_email=customer_email,
                    party_size=party_size,
                    date=date,
                    shift_name=shift.name,
                    shift_start=shift.start_time,
                    shift_end=shift.end_time,
                    special_requests=special_requests,
                    status="confirmed",
                    channel=channel,
                    language=language,
                    created_at=now,
                    updated_at=now,
                )
                await reservation.insert()
                return {
                    "success": True,
                    "reservation_id": str(reservation.id),
                    "table_number": reservation.table_number,
                    "date": date,
                    "shift": shift.name,
                    "party_size": party_size,
                    "message": f"Rezervasyon oluşturuldu. Masalar birleştirildi: {reservation.table_number} ({reservation.combined_capacity} kişilik kapasite).",
                }
            return {
                "success": False,
                "message": f"{date} {shift.name} için {party_size} kişilik müsait masa yok.",
            }
        table = min(candidates, key=lambda t: t.capacity)

        now = datetime.utcnow()
        reservation = Reservation(
            business_id=str(self.business.id),
            table_id=table.id,
            table_number=table.number,
            table_section=table.section,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            party_size=party_size,
            date=date,
            shift_name=shift.name,
            shift_start=shift.start_time,
            shift_end=shift.end_time,
            special_requests=special_requests,
            status="confirmed",
            channel=conversation.channel if conversation else "web",
            language=conversation.language if conversation else "tr",
            created_at=now,
            updated_at=now,
        )
        await reservation.insert()

        # Upsert customer record
        await customer_service.upsert_customer(
            business_id=str(self.business.id),
            phone=customer_phone,
            name=customer_name,
            email=customer_email,
        )

        return {
            "success": True,
            "reservation_id": str(reservation.id),
            "table_number": table.number,
            "table_section": table.section,
            "table_capacity": table.capacity,
            "party_size": party_size,
            "date": date,
            "shift": shift.name,
            "shift_start": shift.start_time,
            "shift_end": shift.end_time,
            "message": (
                f"Rezervasyon oluşturuldu! {date} tarihinde {shift.name} ({shift.start_time}–{shift.end_time}), "
                f"{table.section} bölümünde Masa {table.number} ({table.capacity} kişilik), "
                f"{party_size} kişi. Rezervasyon ID: {reservation.id}"
            ),
        }

    async def _cancel_reservation(self, args: dict, conversation: Conversation) -> dict:
        """Cancel a reservation by ID (phone validation)."""
        reservation_id = args.get("reservation_id", "")
        customer_phone = args.get("customer_phone", "")

        if not reservation_id:
            return {"error": "reservation_id gerekli."}

        try:
            reservation = await Reservation.get(reservation_id)
        except Exception:
            reservation = None

        if not reservation or reservation.business_id != str(self.business.id):
            return {"error": "Rezervasyon bulunamadı."}

        if customer_phone and reservation.customer_phone != customer_phone:
            return {"error": "Telefon numarası rezervasyon kaydıyla eşleşmiyor."}

        if reservation.status in ("cancelled", "completed"):
            return {"error": f"Rezervasyon zaten {reservation.status} durumunda."}

        reservation.status = "cancelled"
        reservation.updated_at = datetime.utcnow()
        await reservation.save()

        return {
            "success": True,
            "message": (
                f"{reservation.date} {reservation.shift_name} Masa {reservation.table_number} "
                f"rezervasyonunuz iptal edildi."
            ),
        }
