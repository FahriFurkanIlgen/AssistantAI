"""
AI Service - GPT-4o powered appointment scheduling assistant.
Uses OpenAI function calling to check availability and create appointments.
"""
from openai import AsyncOpenAI
from typing import Optional
import json
from datetime import datetime, timedelta
import pytz

from app.config import settings
from app.models.business import Business
from app.models.conversation import Conversation, Message

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# ── Sector-specific system prompts ──────────────────────────────────────────

SECTOR_PROMPTS = {
    "tattoo": {
        "tr": (
            "Sen {business_name} dövme stüdyosunun yapay zeka asistanısın, adın {persona_name}. "
            "Müşterileri samimi ve arkadaşça karşılıyorsun. "
            "Görevin: müşterinin istediği dövme hizmeti, tercih ettiği tarih ve saat bilgisini alarak "
            "randevu oluşturmak. Önce müşterinin adını ve telefon numarasını öğren, "
            "ardından istediği hizmeti ve tarih/saat tercihini sor. "
            "Müsaitlik kontrolü yap, uygun slotları sun ve randevuyu onayla. "
            "Kısa ve net cevaplar ver. Emoji kullanabilirsin."
        ),
        "en": (
            "You are the AI assistant of {business_name} tattoo studio, your name is {persona_name}. "
            "Greet customers warmly and in a friendly manner. "
            "Your goal: collect the customer's desired tattoo service, preferred date and time, "
            "then create an appointment. First get the customer's name and phone number, "
            "then ask for the desired service and date/time preference. "
            "Check availability, present suitable slots and confirm the appointment. "
            "Keep answers short and clear. You can use emojis."
        ),
    },
    "doctor": {
        "tr": (
            "Sen {business_name} kliniğinin yapay zeka randevu asistanısın, adın {persona_name}. "
            "Hastalara profesyonel ve anlayışlı bir tutumla yaklaş. "
            "Görevin: hastanın şikayetini/muayene talebini, tercih ettiği tarih ve saati alarak "
            "randevu oluşturmak. Önce hastanın adını ve telefon numarasını öğren. "
            "Müsaitlik kontrolü yaparak randevuyu onayla."
        ),
        "en": (
            "You are the AI appointment assistant of {business_name} clinic, your name is {persona_name}. "
            "Approach patients professionally and empathetically. "
            "Your goal: collect the patient's complaint/exam request, preferred date and time, "
            "then create an appointment. First get the patient's name and phone number. "
            "Check availability and confirm the appointment."
        ),
    },
    "beauty": {
        "tr": (
            "Sen {business_name} güzellik merkezinin yapay zeka asistanısın, adın {persona_name}. "
            "Müşterileri sıcak ve enerjik bir şekilde karşıla. "
            "Görevin: müşterinin istediği güzellik hizmetini, tercih ettiği tarih ve saati alarak "
            "randevu oluşturmak. Önce müşterinin adını ve telefon numarasını öğren. "
            "Müsaitlik kontrolü yaparak randevuyu onayla. ✨"
        ),
        "en": (
            "You are the AI assistant of {business_name} beauty center, your name is {persona_name}. "
            "Greet customers warmly and energetically. "
            "Your goal: collect the customer's desired beauty service, preferred date and time, "
            "then create an appointment. First get the customer's name and phone number. "
            "Check availability and confirm the appointment. ✨"
        ),
    },
    "general": {
        "tr": (
            "Sen {business_name} işletmesinin yapay zeka randevu asistanısın, adın {persona_name}. "
            "Müşterileri nazikçe karşıla ve randevu oluşturma sürecinde yardımcı ol. "
            "Önce müşterinin adını ve telefon numarasını öğren, "
            "ardından istediği hizmeti ve tarih/saat tercihini sor."
        ),
        "en": (
            "You are the AI appointment assistant of {business_name}, your name is {persona_name}. "
            "Greet customers politely and assist with the appointment booking process. "
            "First get the customer's name and phone number, "
            "then ask for the desired service and date/time preference."
        ),
    },
}

# ── Tool definitions (function calling) ─────────────────────────────────────

APPOINTMENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check available appointment slots for a given date range. "
                "Returns a list of available time slots."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to check in YYYY-MM-DD format",
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration of the appointment in minutes",
                        "default": 60,
                    },
                },
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "Create a new appointment after collecting all required information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Full name of the customer",
                    },
                    "customer_phone": {
                        "type": "string",
                        "description": "Phone number of the customer",
                    },
                    "customer_email": {
                        "type": "string",
                        "description": "Email address of the customer (optional)",
                    },
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service requested",
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "Start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration of the appointment in minutes",
                        "default": 60,
                    },
                    "notes": {
                        "type": "string",
                        "description": "Any additional notes or special requests from the customer",
                    },
                    "staff_id": {
                        "type": "string",
                        "description": "ID of the staff member to book with (optional, from get_staff_list)",
                    },
                    "staff_name": {
                        "type": "string",
                        "description": "Name of the staff member to book with (optional, for display)",
                    },
                },
                "required": ["customer_name", "customer_phone", "service_name", "start_datetime"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_services",
            "description": "Get the list of available services offered by the business.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_cancel_otp",
            "description": (
                "When a customer wants to cancel their appointment, look it up by phone number "
                "and send a 6-digit OTP code to their email address. "
                "Call this ONLY after confirming the customer's phone number."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_phone": {
                        "type": "string",
                        "description": "Phone number of the customer whose appointment should be found",
                    },
                },
                "required": ["customer_phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_cancel_appointment",
            "description": (
                "Verify the OTP code entered by the customer and cancel the appointment. "
                "Call this after the customer provides the 6-digit code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "ID of the appointment to cancel (returned by request_cancel_otp)",
                    },
                    "otp_code": {
                        "type": "string",
                        "description": "6-digit OTP code entered by the customer",
                    },
                },
                "required": ["appointment_id", "otp_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_staff_list",
            "description": (
                "Get the list of active staff members (employees) of the business, "
                "along with the services each one offers. "
                "Call this when the business has multiple staff members and the customer "
                "needs to choose who to book with."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ── Main AI service ──────────────────────────────────────────────────────────

class AIService:
    def __init__(self, business: Business, tool_executor):
        self.business = business
        self.tool_executor = tool_executor  # async callable that executes tool calls

    def _build_system_prompt(self, language: str) -> str:
        sector = self.business.sector
        lang_key = language if language in ("tr", "en") else "tr"

        template = SECTOR_PROMPTS.get(sector, SECTOR_PROMPTS["general"])[lang_key]
        base_prompt = template.format(
            business_name=self.business.name,
            persona_name=self.business.ai_persona_name,
        )

        # Append custom instructions if provided
        if self.business.custom_ai_instructions:
            base_prompt += f"\n\nEk talimatlar: {self.business.custom_ai_instructions}"

        # Append working hours context
        today = datetime.utcnow()
        base_prompt += (
            f"\n\nBugünün tarihi: {today.strftime('%Y-%m-%d')} ({today.strftime('%A')}). "
            "Tarih/saat bilgisi alırken bu bilgiyi kullan."
        )

        # Append working schedule so bot can validate before asking personal info
        ws = self.business.working_schedule
        if ws:
            day_names = {
                "monday": "Pazartesi", "tuesday": "Salı", "wednesday": "Çarşamba",
                "thursday": "Perşembe", "friday": "Cuma", "saturday": "Cumartesi", "sunday": "Pazar"
            }
            schedule_lines = []
            for day_en, day_tr in day_names.items():
                hours = getattr(ws, day_en, None)
                if hours:
                    if hours.is_open:
                        schedule_lines.append(f"  {day_tr}: {hours.start}–{hours.end}")
                    else:
                        schedule_lines.append(f"  {day_tr}: KAPALI")
            schedule_str = "\n".join(schedule_lines)
            base_prompt += (
                f"\n\nÇALIŞMA SAATLERİ:\n{schedule_str}\n"
                "KURALLAR (çok önemli – sırayla uygula):\n"
                "1) Müşterinin istediği tarih/saati önce yukarıdaki çalışma saatleri ile KENDİN karşılaştır. "
                "İstenen gün KAPALI ise veya saat o günün start–end aralığının DIŞINDA ise, "
                "kişisel bilgi SORMADAN 'O gün/saat müsait değiliz' diyerek reddet ve alternatif öner. "
                "Yukarıdaki listede AÇIK olarak gösterilen bir gün ve aralıktaki bir saat için ASLA 'o gün kapalıyız/müsait değiliz' deme. "
                "(Örn: Cuma 09:00–18:00 açıksa, 'Cuma sabah 10:00' talebine 'kapalıyız' demek YANLIŞTIR.)\n"
                "2) İstenen tarih/saat çalışma saatleri içindeyse, müsaitlik için MUTLAKA `check_availability` aracını çağır. "
                "Tool çağırmadan slot var/yok kararı verme.\n"
                "3) `check_availability` boş döndüyse o saat dolu demektir; başka müsait slotları öner. "
                "Çalışma saati içinde olduğu halde 'kapalıyız' deme.\n"
                "4) Göreli tarih ifadelerini (\"yarın\", \"önümüzdeki hafta cuma\" vb.) yukarıda verilen bugünün tarihine göre hesapla "
                "ve çalışma takvimine göre doğrula."
            )

        # Vision instruction
        base_prompt += (
            "\n\nEğer kullanıcı bir görsel paylaşırsa, görseli analiz et ve stil/model önerisi yap. "
            "Dövme stüdyosu için: stil (geometrik, realism, minimalist, blackwork, watercolor vb.) ve uygun beden bölgesi öner. "
            "Güzellik merkezi için: renk paleti, saç stili veya makyaj önerisi yap."
        )

        # Cancellation OTP flow instruction
        base_prompt += (
            "\n\nRANDEVU İPTAL AKIŞI: Müşteri randevusunu iptal etmek istediğinde:\n"
            "1. Müşterinin telefon numarasını sor.\n"
            "2. `request_cancel_otp` aracını çağır — sistem OTP kodunu müşterinin e-postasına gönderecek ve randevu bilgilerini döndürecek.\n"
            "3. Müşteriden e-postasına gelen 6 haneli kodu girmesini iste.\n"
            "4. `confirm_cancel_appointment` aracını çağır — kod doğruysa randevu iptal edilir.\n"
            "E-posta adresi yoksa müşteriye bildirip işletmeyle iletişime geçmelerini söyle."
        )

        # Returning customer context
        base_prompt += (
            "\n\nTEKRAR MÜŞTERI: Müşteri sana telefon numarasını söylediğinde, randevu oluşturma sırasında "
            "aynı numaranın daha önce kullanılıp kullanılmadığına bakabilirsin. Eğer daha önce randevu oluşturduysa, "
            "adını zaten biliyorsundur — 'Tekrar hoş geldiniz [isim]!' şeklinde karşıla ve "
            "yeniden isim sormana gerek yok."
        )

        # Staff selection context (async staff check happens at runtime via get_staff_list tool)
        base_prompt += (
            "\n\nPERSONEL SEÇİMİ: Eğer işletmenin birden fazla çalışanı varsa, "
            "müşteri randevu almak istediğinde `get_staff_list` aracını çağırarak aktif personelleri listele. "
            "Personel listesi boş değilse müşteriye hangi personelle randevu almak istediğini sor. "
            "Müşteri tercih belirtmezse 'herhangi biri' seçeneğini sun ve staff_id olmadan randevu oluştur. "
            "Personel seçildikten sonra `check_availability` aracını o personelin staff_id'si ile çağır."
        )

        # Instagram portfolio context
        if self.business.instagram_handle:
            handle = self.business.instagram_handle.lstrip("@")
            base_prompt += (
                f"\n\nİşletmenin Instagram portfolyosu: @{handle} "
                f"(https://www.instagram.com/{handle}/). "
                "Müşteriler stil veya örnek sorduktan sonra bu hesabı ziyaret etmelerini öner. "
                "Chat üzerinden portfolyo görsellerini de gösterebilirsin."
            )

        return base_prompt

    async def process_message(
        self,
        conversation: Conversation,
        user_message: str,
        language: str = "tr",
        image: Optional[str] = None,
    ) -> str:
        """Process a user message and return the assistant's response."""
        # Add user message to history (plain text only for persistence)
        conversation.messages.append(
            Message(role="user", content=user_message)
        )

        # Build messages for OpenAI
        messages = [{"role": "system", "content": self._build_system_prompt(language)}]
        for msg in conversation.messages[:-1]:
            entry: dict = {"role": msg.role, "content": msg.content}
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            messages.append(entry)

        # Build the current user message — with optional vision content
        if image:
            user_content: list | str = [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": image, "detail": "auto"}},
            ]
        else:
            user_content = user_message
        messages.append({"role": "user", "content": user_content})

        # Agentic loop – keep calling until no more tool calls
        while True:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                tools=APPOINTMENT_TOOLS,
                tool_choice="auto",
                temperature=0.7,
            )

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                assistant_msg = choice.message
                # Append assistant's tool-call message
                tool_calls_raw = [tc.model_dump() for tc in assistant_msg.tool_calls]
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_msg.content,
                        "tool_calls": tool_calls_raw,
                    }
                )
                conversation.messages.append(
                    Message(
                        role="assistant",
                        content=assistant_msg.content or "",
                        tool_calls=tool_calls_raw,
                    )
                )

                # Execute each tool call
                for tool_call in assistant_msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    tool_result = await self.tool_executor(fn_name, fn_args, conversation)
                    tool_result_str = json.dumps(tool_result, ensure_ascii=False)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result_str,
                        }
                    )
                    conversation.messages.append(
                        Message(
                            role="tool",
                            content=tool_result_str,
                            tool_call_id=tool_call.id,
                        )
                    )
            else:
                # Final text response
                final_text = choice.message.content or ""
                conversation.messages.append(
                    Message(role="assistant", content=final_text)
                )
                await conversation.save()
                return final_text
