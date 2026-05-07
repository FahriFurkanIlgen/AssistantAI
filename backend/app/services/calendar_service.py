"""
Google Calendar Service - OAuth2 integration for appointment sync.
"""
import json
from datetime import datetime, timedelta
from typing import List, Optional
import pytz

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

from app.config import settings
from app.models.business import Business

SCOPES = ["https://www.googleapis.com/auth/calendar"]

GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}


def get_oauth_flow() -> Flow:
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
    return flow


def get_authorization_url(state: str) -> str:
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent",
    )
    return auth_url


def exchange_code_for_tokens(code: str) -> dict:
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
    }


def _build_credentials(business: Business) -> Optional[Credentials]:
    if not business.google_refresh_token:
        return None

    creds = Credentials(
        token=business.google_access_token,
        refresh_token=business.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


class CalendarService:
    def __init__(self, business: Business):
        self.business = business
        self._service = None

    def _get_service(self):
        if self._service is None:
            creds = _build_credentials(self.business)
            if creds is None:
                raise ValueError("Google Calendar bağlantısı yapılmamış. Lütfen işletme ayarlarından bağlayın.")
            self._service = build("calendar", "v3", credentials=creds)
        return self._service

    def get_calendar_id(self) -> str:
        return self.business.google_calendar_id or "primary"

    def get_busy_slots(self, date: str) -> List[dict]:
        """Return busy time blocks for a given date (YYYY-MM-DD)."""
        service = self._get_service()
        tz = pytz.UTC

        day_start = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=0, minute=0, second=0, tzinfo=tz
        )
        day_end = day_start + timedelta(days=1)

        body = {
            "timeMin": day_start.isoformat(),
            "timeMax": day_end.isoformat(),
            "items": [{"id": self.get_calendar_id()}],
        }
        freebusy = service.freebusy().query(body=body).execute()
        calendars = freebusy.get("calendars", {})
        busy = calendars.get(self.get_calendar_id(), {}).get("busy", [])
        return busy

    def get_available_slots(self, date: str, duration_minutes: int = 60) -> List[str]:
        """Return list of available start times (HH:MM) for a given date."""
        from app.models.business import WorkingHours

        # Map day name to schedule field
        day_name_map = {
            "Monday": "monday",
            "Tuesday": "tuesday",
            "Wednesday": "wednesday",
            "Thursday": "thursday",
            "Friday": "friday",
            "Saturday": "saturday",
            "Sunday": "sunday",
        }

        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        schedule_key = day_name_map.get(day_name, "monday")
        day_schedule: WorkingHours = getattr(
            self.business.working_schedule, schedule_key
        )

        if not day_schedule.is_open:
            return []

        # Build candidate slots (30-minute increments)
        open_h, open_m = map(int, day_schedule.start.split(":"))
        close_h, close_m = map(int, day_schedule.end.split(":"))

        slot_start = date_obj.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
        closing_time = date_obj.replace(hour=close_h, minute=close_m, second=0, microsecond=0)

        candidates = []
        while slot_start + timedelta(minutes=duration_minutes) <= closing_time:
            candidates.append(slot_start)
            slot_start += timedelta(minutes=30)

        # Remove slots that overlap with busy periods
        try:
            busy = self.get_busy_slots(date)
        except Exception:
            busy = []

        tz = pytz.UTC
        busy_ranges = []
        for b in busy:
            bs = datetime.fromisoformat(b["start"].replace("Z", "+00:00")).astimezone(tz)
            be = datetime.fromisoformat(b["end"].replace("Z", "+00:00")).astimezone(tz)
            busy_ranges.append((bs.replace(tzinfo=None), be.replace(tzinfo=None)))

        available = []
        for slot in candidates:
            slot_end = slot + timedelta(minutes=duration_minutes)
            conflict = any(
                not (slot_end <= bs or slot >= be)
                for bs, be in busy_ranges
            )
            if not conflict:
                available.append(slot.strftime("%H:%M"))

        return available

    def create_event(
        self,
        summary: str,
        start_datetime: str,
        duration_minutes: int,
        description: Optional[str] = None,
        attendee_email: Optional[str] = None,
    ) -> dict:
        """Create a Google Calendar event and return the event dict."""
        service = self._get_service()

        start_dt = datetime.fromisoformat(start_datetime)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event_body = {
            "summary": summary,
            "description": description or "",
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "UTC",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        if attendee_email:
            event_body["attendees"] = [{"email": attendee_email}]

        created = (
            service.events()
            .insert(calendarId=self.get_calendar_id(), body=event_body, sendUpdates="all")
            .execute()
        )
        return created

    def delete_event(self, event_id: str) -> bool:
        """Delete a Google Calendar event by ID."""
        try:
            service = self._get_service()
            service.events().delete(
                calendarId=self.get_calendar_id(), eventId=event_id
            ).execute()
            return True
        except Exception:
            return False
