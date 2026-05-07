"""
Appointment Service - Handles all appointment CRUD and the AI tool executor.
"""
from datetime import datetime
from typing import Optional
from bson import ObjectId

from app.models.appointment import Appointment
from app.models.business import Business
from app.models.conversation import Conversation
from app.services.calendar_service import CalendarService


class AppointmentService:
    def __init__(self, business: Business):
        self.business = business
        self.calendar = CalendarService(business)

    # ── AI Tool Executor ────────────────────────────────────────────────────

    async def execute_tool(self, fn_name: str, fn_args: dict, conversation: Conversation) -> dict:
        """Route tool calls coming from the AI service."""
        if fn_name == "get_services":
            return self._get_services()
        elif fn_name == "check_availability":
            return self._check_availability(
                date=fn_args.get("date"),
                duration_minutes=fn_args.get("duration_minutes", self.business.default_appointment_duration),
            )
        elif fn_name == "create_appointment":
            return await self._create_appointment(fn_args, conversation)
        else:
            return {"error": f"Unknown tool: {fn_name}"}

    # ── Tool implementations ────────────────────────────────────────────────

    def _get_services(self) -> dict:
        if not self.business.services:
            return {
                "services": [],
                "message": "Hizmet listesi henüz eklenmemiş. Genel randevu oluşturabilirsiniz.",
            }
        return {
            "services": [
                {
                    "name": s.name,
                    "name_tr": s.name_tr,
                    "duration_minutes": s.duration_minutes,
                    "price": s.price,
                    "description": s.description,
                }
                for s in self.business.services
            ]
        }

    def _check_availability(self, date: str, duration_minutes: int) -> dict:
        try:
            slots = self.calendar.get_available_slots(date, duration_minutes)
            if not slots:
                return {
                    "date": date,
                    "available": False,
                    "slots": [],
                    "message": f"{date} tarihinde müsait slot bulunamadı.",
                }
            return {
                "date": date,
                "available": True,
                "slots": slots,
                "message": f"{date} tarihinde şu saatler müsait: {', '.join(slots)}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def _create_appointment(self, args: dict, conversation: Conversation) -> dict:
        try:
            customer_name = args["customer_name"]
            customer_phone = args["customer_phone"]
            customer_email = args.get("customer_email")
            service_name = args["service_name"]
            start_datetime_str = args["start_datetime"]
            duration_minutes = args.get("duration_minutes", self.business.default_appointment_duration)
            notes = args.get("notes")

            start_dt = datetime.fromisoformat(start_datetime_str)
            end_dt = start_dt + __import__("datetime").timedelta(minutes=duration_minutes)

            # Create Google Calendar event
            google_event_id = None
            try:
                event_summary = f"{service_name} – {customer_name}"
                event_description = f"Müşteri: {customer_name}\nTelefon: {customer_phone}"
                if notes:
                    event_description += f"\nNot: {notes}"

                gc_event = self.calendar.create_event(
                    summary=event_summary,
                    start_datetime=start_datetime_str,
                    duration_minutes=duration_minutes,
                    description=event_description,
                    attendee_email=customer_email,
                )
                google_event_id = gc_event.get("id")
            except Exception:
                pass  # Calendar not connected – still create DB record

            # Save appointment
            appointment = Appointment(
                business_id=str(self.business.id),
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                service_name=service_name,
                notes=notes,
                start_time=start_dt,
                end_time=end_dt,
                duration_minutes=duration_minutes,
                google_event_id=google_event_id,
                language=conversation.language,
            )
            await appointment.insert()

            # Link appointment to conversation
            conversation.appointment_id = str(appointment.id)
            conversation.customer_name = customer_name
            conversation.customer_phone = customer_phone
            conversation.status = "completed"

            return {
                "success": True,
                "appointment_id": str(appointment.id),
                "customer_name": customer_name,
                "service_name": service_name,
                "start_time": start_dt.strftime("%d.%m.%Y %H:%M"),
                "end_time": end_dt.strftime("%d.%m.%Y %H:%M"),
                "google_calendar_synced": google_event_id is not None,
                "message": (
                    f"Randevu başarıyla oluşturuldu! "
                    f"{start_dt.strftime('%d.%m.%Y %H:%M')} tarihinde {service_name} randevunuz onaylandı."
                ),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── CRUD ────────────────────────────────────────────────────────────────

    async def get_appointments(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        status: Optional[str] = None,
    ):
        query = {"business_id": str(self.business.id)}
        if status:
            query["status"] = status
        if start:
            query["start_time"] = {"$gte": start}
        if end:
            query.setdefault("start_time", {})["$lte"] = end

        return await Appointment.find(query).sort("start_time").to_list()

    async def cancel_appointment(self, appointment_id: str) -> bool:
        appt = await Appointment.get(appointment_id)
        if not appt or str(appt.business_id) != str(self.business.id):
            return False

        appt.status = "cancelled"
        appt.updated_at = datetime.utcnow()
        await appt.save()

        if appt.google_event_id:
            self.calendar.delete_event(appt.google_event_id)

        return True
