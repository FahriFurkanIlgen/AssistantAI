"""
Appointment Service - Handles all appointment CRUD and the AI tool executor.
"""
from datetime import datetime
from typing import Optional
from bson import ObjectId
import random
import asyncio

from app.models.appointment import Appointment
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.otp_code import OtpCode
from app.services.calendar_service import CalendarService
from app.services.email_service import send_confirmation_email


class AppointmentService:
    def __init__(self, business: Business, staff_member=None):
        self.business = business
        self.staff_member = staff_member
        # Use staff's Google Calendar if they have one, otherwise fall back to business
        calendar_holder = (
            staff_member
            if staff_member and staff_member.google_refresh_token
            else business
        )
        self.calendar = CalendarService(calendar_holder)

    # ── AI Tool Executor ────────────────────────────────────────────────────

    async def execute_tool(self, fn_name: str, fn_args: dict, conversation: Conversation) -> dict:
        """Route tool calls coming from the AI service."""
        if fn_name == "get_services":
            return self._get_services(fn_args.get("staff_id"))
        elif fn_name == "get_staff_list":
            return await self._get_staff_list()
        elif fn_name == "check_availability":
            return await self._check_availability_async(
                date=fn_args.get("date"),
                duration_minutes=fn_args.get("duration_minutes", self.business.default_appointment_duration),
                staff_id=fn_args.get("staff_id"),
            )
        elif fn_name == "create_appointment":
            return await self._create_appointment(fn_args, conversation)
        elif fn_name == "request_cancel_otp":
            return await self._request_cancel_otp(fn_args.get("customer_phone", ""))
        elif fn_name == "confirm_cancel_appointment":
            return await self._confirm_cancel_appointment(
                fn_args.get("appointment_id", ""),
                fn_args.get("otp_code", ""),
            )
        else:
            return {"error": f"Unknown tool: {fn_name}"}

    # ── Tool implementations ────────────────────────────────────────────────

    def _get_services(self, staff_id: str = None) -> dict:
        services = self.business.services
        # If a staff member is specified, filter to their offered services
        if staff_id:
            from app.models.staff_member import StaffMember
            # Filtering happens async; for sync call use business services as fallback
            pass
        if not services:
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
                for s in services
            ]
        }

    async def _get_staff_list(self) -> dict:
        """Return active staff members with their offered services."""
        from app.models.staff_member import StaffMember
        members = await StaffMember.find(
            StaffMember.business_id == str(self.business.id),
            StaffMember.is_active == True,
        ).to_list()
        if not members:
            return {"staff": [], "message": "Bu işletmede kayıtlı personel bulunamadı."}
        return {
            "staff": [
                {
                    "id": str(m.id),
                    "name": m.name,
                    "service_names": m.service_names,
                }
                for m in members
            ]
        }

    async def _check_availability_async(
        self, date: str, duration_minutes: int, staff_id: str = None
    ) -> dict:
        """Async wrapper for availability check; uses staff schedule if staff_id given."""
        try:
            if staff_id:
                from app.models.staff_member import StaffMember
                staff = await StaffMember.get(staff_id)
                if staff and staff.business_id == str(self.business.id) and staff.is_active:
                    # Use staff's own schedule and calendar
                    staff_calendar = CalendarService(staff)
                    slots = staff_calendar.get_available_slots(date, duration_minutes)
                else:
                    slots = self.calendar.get_available_slots(date, duration_minutes)
            else:
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

    def _check_availability(self, date: str, duration_minutes: int) -> dict:
        """Sync availability check using the default calendar (business or pre-set staff)."""
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
            staff_id = args.get("staff_id")
            staff_name = args.get("staff_name")

            # Resolve staff name from DB if only id given
            if staff_id and not staff_name:
                from app.models.staff_member import StaffMember
                staff_obj = await StaffMember.get(staff_id)
                if staff_obj:
                    staff_name = staff_obj.name

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
                staff_id=staff_id,
                staff_name=staff_name,
            )
            await appointment.insert()

            # Send confirmation email (fire-and-forget)
            if customer_email:
                loop = asyncio.get_event_loop()
                loop.run_in_executor(
                    None,
                    send_confirmation_email,
                    customer_email,
                    customer_name,
                    service_name,
                    start_dt.strftime("%d.%m.%Y %H:%M"),
                    end_dt.strftime("%d.%m.%Y %H:%M"),
                    self.business.name,
                    self.business.phone or "",
                )

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
        staff_id: Optional[str] = None,
    ):
        query = {"business_id": str(self.business.id)}
        if status:
            query["status"] = status
        if staff_id:
            query["staff_id"] = staff_id
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

    # ── OTP cancel flow ──────────────────────────────────────────────────────

    async def _request_cancel_otp(self, customer_phone: str) -> dict:
        """Find active appointment by phone, generate OTP and send email."""
        from app.services.email_service import send_cancel_otp_email

        # Normalize phone
        phone = customer_phone.strip()

        # Find the most recent confirmed appointment for this phone under this business
        appt = await Appointment.find_one(
            {
                "business_id": str(self.business.id),
                "customer_phone": phone,
                "status": {"$in": ["confirmed", "pending"]},
            },
            sort=[("start_time", -1)],
        )

        if not appt:
            return {
                "success": False,
                "error": (
                    "Bu telefon numarasına ait aktif bir randevu bulunamadı. "
                    "Lütfen numarayı kontrol edin."
                ),
            }

        if not appt.customer_email:
            return {
                "success": False,
                "appointment_id": str(appt.id),
                "error": (
                    "Randevunuzda e-posta adresi kayıtlı değil. "
                    "İptal için lütfen işletmeyle doğrudan iletişime geçin."
                ),
            }

        # Generate 6-digit OTP
        code = f"{random.randint(100000, 999999)}"

        # Invalidate any existing OTPs for this appointment
        await OtpCode.find(
            {"appointment_id": str(appt.id), "used": False}
        ).update({"$set": {"used": True}})

        otp = OtpCode.generate(
            appointment_id=str(appt.id),
            email=appt.customer_email,
            code=code,
        )
        await otp.insert()

        appointment_summary = (
            f"{appt.service_name} — "
            f"{appt.start_time.strftime('%d.%m.%Y %H:%M')}"
        )

        # Send email in background (don't block chat response)
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: send_cancel_otp_email(
                    to_email=appt.customer_email,
                    customer_name=appt.customer_name,
                    appointment_summary=appointment_summary,
                    otp_code=code,
                    business_name=self.business.name,
                ),
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"E-posta gönderilemedi: {str(e)}. SMTP ayarlarını kontrol edin.",
            }

        return {
            "success": True,
            "appointment_id": str(appt.id),
            "appointment_summary": appointment_summary,
            "email_hint": appt.customer_email[:3] + "***@" + appt.customer_email.split("@")[-1],
            "message": (
                f"OTP kodu {appt.customer_email[:3]}***@{appt.customer_email.split('@')[-1]} "
                f"adresine gönderildi. Lütfen e-postanıza gelen 6 haneli kodu girin."
            ),
        }

    async def _confirm_cancel_appointment(self, appointment_id: str, otp_code: str) -> dict:
        """Verify OTP and cancel the appointment."""
        otp = await OtpCode.find_one(
            {"appointment_id": appointment_id, "used": False}
        )

        if not otp:
            return {"success": False, "error": "Geçersiz veya süresi dolmuş kod."}

        if not otp.is_valid():
            return {"success": False, "error": "Kodun süresi dolmuş. Lütfen tekrar deneyin."}

        if otp.code != otp_code.strip():
            return {"success": False, "error": "Girdiğiniz kod hatalı. Lütfen tekrar deneyin."}

        # Mark OTP as used
        otp.used = True
        await otp.save()

        # Cancel appointment
        appt = await Appointment.get(appointment_id)
        if not appt:
            return {"success": False, "error": "Randevu bulunamadı."}

        appt.status = "cancelled"
        appt.updated_at = datetime.utcnow()
        await appt.save()

        # Delete from Google Calendar if connected
        if appt.google_event_id:
            try:
                self.calendar.delete_event(appt.google_event_id)
            except Exception:
                pass

        return {
            "success": True,
            "message": (
                f"Randevunuz başarıyla iptal edildi. "
                f"{appt.service_name} — {appt.start_time.strftime('%d.%m.%Y %H:%M')} "
                f"tarihli randevunuz iptal edilmiştir."
            ),
        }
