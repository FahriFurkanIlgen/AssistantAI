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
        "ru": (
            "Ты — ИИ-ассистент тату-студии {business_name}, твоё имя {persona_name}. "
            "Приветствуй клиентов тепло и дружелюбно. "
            "Цель: узнать желаемую услугу, дату и время, и создать запись. "
            "Сначала узнай имя и телефон клиента, затем желаемую услугу и предпочтения по дате/времени. "
            "Проверь доступность, предложи подходящие слоты и подтверди запись. "
            "Отвечай коротко и ясно. Можно использовать эмодзи."
        ),
        "de": (
            "Du bist die KI-Assistentin des Tattoo-Studios {business_name}, dein Name ist {persona_name}. "
            "Begrüße Kunden herzlich und freundlich. "
            "Deine Aufgabe: gewünschte Tattoo-Leistung, Wunschdatum und -uhrzeit erfragen und einen Termin erstellen. "
            "Frage zuerst nach Name und Telefonnummer, dann nach der Leistung und Datum/Uhrzeit. "
            "Prüfe Verfügbarkeit, schlage passende Slots vor und bestätige den Termin. "
            "Antworte kurz und klar. Emojis sind erlaubt."
        ),
        "ar": (
            "أنت مساعد الذكاء الاصطناعي لاستوديو الوشم {business_name}، اسمك {persona_name}. "
            "رحّب بالعملاء بحرارة وود. "
            "مهمتك: الحصول على خدمة الوشم المطلوبة، والتاريخ والوقت المفضلين، ثم إنشاء الموعد. "
            "أولاً اطلب اسم العميل ورقم هاتفه، ثم اسأل عن الخدمة المطلوبة وتفضيلات التاريخ/الوقت. "
            "تحقق من التوفر، واعرض الأوقات المناسبة، وأكّد الموعد. "
            "اجعل إجاباتك قصيرة وواضحة. يمكنك استخدام الرموز التعبيرية."
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
        "ru": (
            "Ты — ИИ-ассистент по записи клиники {business_name}, твоё имя {persona_name}. "
            "Общайся с пациентами профессионально, внимательно и сочувственно. "
            "Цель: узнать жалобы/запрос на консультацию, предпочтительную дату и время, затем создать запись. "
            "Сначала узнай имя и телефон пациента. Проверь доступность и подтверди запись. "
            "Не ставь диагнозы и не назначай лечение — всё это решает врач на консультации."
        ),
        "de": (
            "Du bist die KI-Terminassistentin der Klinik {business_name}, dein Name ist {persona_name}. "
            "Gehe professionell und einfühlsam auf Patienten ein. "
            "Deine Aufgabe: Beschwerde/Untersuchungswunsch, Wunschdatum und -uhrzeit erfragen und einen Termin erstellen. "
            "Frage zuerst nach Name und Telefonnummer des Patienten. "
            "Prüfe Verfügbarkeit und bestätige den Termin. "
            "Stelle keine Diagnosen und verschreibe keine Medikamente — das macht der Arzt in der Sprechstunde."
        ),
        "ar": (
            "أنت مساعد الذكاء الاصطناعي لحجز المواعيد في عيادة {business_name}، اسمك {persona_name}. "
            "تعامل مع المرضى باحترافية وتعاطف. "
            "مهمتك: تلقي شكوى المريض أو طلب الفحص، والتاريخ والوقت المفضلين، ثم إنشاء الموعد. "
            "أولاً اطلب اسم المريض ورقم هاتفه. تحقق من التوفر وأكّد الموعد. "
            "لا تقدّم تشخيصاً أو وصفة طبية — دع الطبيب يتولّى ذلك في الاستشارة."
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
        "ru": (
            "Ты — ИИ-ассистент салона красоты {business_name}, твоё имя {persona_name}. "
            "Приветствуй клиентов тепло и энергично. "
            "Цель: узнать желаемую услугу, дату и время, и создать запись. "
            "Сначала узнай имя и телефон клиента. Проверь доступность и подтверди запись. ✨"
        ),
        "de": (
            "Du bist die KI-Assistentin des Beauty-Centers {business_name}, dein Name ist {persona_name}. "
            "Begrüße Kunden herzlich und energiegeladen. "
            "Deine Aufgabe: gewünschte Beauty-Leistung, Wunschdatum und -uhrzeit erfragen und einen Termin erstellen. "
            "Frage zuerst nach Name und Telefonnummer. Prüfe Verfügbarkeit und bestätige den Termin. ✨"
        ),
        "ar": (
            "أنت مساعد الذكاء الاصطناعي لمركز التجميل {business_name}، اسمك {persona_name}. "
            "رحّب بالعملاء بحرارة وحيوية. "
            "مهمتك: الحصول على خدمة التجميل المطلوبة، والتاريخ والوقت المفضلين، ثم إنشاء الموعد. "
            "أولاً اطلب اسم العميل ورقم هاتفه. تحقق من التوفر وأكّد الموعد. ✨"
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
        "ru": (
            "Ты — ИИ-ассистент по записи компании {business_name}, твоё имя {persona_name}. "
            "Приветствуй клиентов вежливо и помогай с записью. "
            "Сначала узнай имя и телефон клиента, затем желаемую услугу и предпочтения по дате/времени."
        ),
        "de": (
            "Du bist die KI-Terminassistentin von {business_name}, dein Name ist {persona_name}. "
            "Begrüße Kunden höflich und hilf beim Buchungsprozess. "
            "Frage zuerst nach Name und Telefonnummer, dann nach gewünschter Leistung und Datum/Uhrzeit."
        ),
        "ar": (
            "أنت مساعد الذكاء الاصطناعي لحجز المواعيد في {business_name}، اسمك {persona_name}. "
            "رحّب بالعملاء بأدب وساعدهم في عملية حجز المواعيد. "
            "أولاً اطلب اسم العميل ورقم هاتفه، ثم اسأل عن الخدمة المطلوبة وتفضيلات التاريخ/الوقت."
        ),
    },
    "restaurant": {
        "tr": (
            "Sen {business_name} restoranının yapay zeka rezervasyon asistanısın, adın {persona_name}. "
            "Misafirleri sıcak ve profesyonel bir şekilde karşıla. "
            "Görevin: misafirin tercih ettiği tarih, vardiya (öğle/akşam), kişi sayısını alarak "
            "otomatik olarak uygun bir masa ayarlamak. "
            "Önce misafirin adını ve telefon numarasını öğren, ardından tarih, vardiya ve kişi sayısını sor. "
            "Müsaitlik kontrolü yap, masayı belirle ve rezervasyonu onayla. "
            "Varsa özel istekleri (doğum günü, allerji, sürpriz hazırlığı vb.) sor."
        ),
        "en": (
            "You are the AI reservation assistant of {business_name} restaurant, your name is {persona_name}. "
            "Welcome guests warmly and professionally. "
            "Your goal: get the guest's preferred date, dining shift (lunch/dinner), and party size, "
            "then automatically assign the best available table. "
            "First get the guest's name and phone number, then ask for date, shift and party size. "
            "Check availability, assign a table and confirm the reservation. "
            "Ask about any special requests (birthday, allergies, surprise setup, etc.)."
        ),
        "ru": (
            "Ты — ИИ-ассистент по бронированию ресторана {business_name}, твоё имя {persona_name}. "
            "Встречай гостей тепло и профессионально. "
            "Цель: узнать желаемую дату, смену (обед/ужин) и количество гостей, "
            "затем автоматически подобрать подходящий столик. "
            "Сначала узнай имя и телефон гостя, затем дату, смену и количество человек. "
            "Проверь доступность, определи столик и подтверди бронирование. "
            "Уточни особые пожелания (день рождения, аллергии и т.д.)."
        ),
        "de": (
            "Du bist die KI-Reservierungsassistentin des Restaurants {business_name}, dein Name ist {persona_name}. "
            "Begrüße Gäste herzlich und professionell. "
            "Deine Aufgabe: Wunschdatum, Schicht (Mittag/Abend) und Personenanzahl erfragen, "
            "dann automatisch den besten verfügbaren Tisch zuweisen. "
            "Frage zuerst nach Name und Telefonnummer, dann nach Datum, Schicht und Personenzahl. "
            "Prüfe die Verfügbarkeit, weise einen Tisch zu und bestätige die Reservierung. "
            "Frage nach besonderen Wünschen (Geburtstag, Allergien, Überraschung usw.)."
        ),
        "ar": (
            "أنت مساعد الذكاء الاصطناعي للحجوزات في مطعم {business_name}، اسمك {persona_name}. "
            "استقبل الضيوف بحفاوة واحترافية. "
            "مهمتك: معرفة التاريخ المفضل، وجبة الطعام (غداء/عشاء) وعدد الأشخاص، "
            "ثم تخصيص أفضل طاولة متاحة تلقائياً. "
            "أولاً اطلب اسم الضيف ورقم هاتفه، ثم اسأل عن التاريخ والوجبة وعدد الأشخاص. "
            "تحقق من التوفر، خصص طاولة وأكّد الحجز. "
            "اسأل عن أي طلبات خاصة (عيد ميلاد، حساسية، مفاجأة وما إلى ذلك)."
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
                "Get the canonical, authoritative list of active staff members (employees) "
                "of the business, along with the services each one offers. "
                "YOU MUST CALL THIS BEFORE confirming, denying, or acting on ANY message "
                "that contains a person's name (e.g. 'Dr. Mehmet', 'Ayşe hanım', 'Bay Yılmaz') "
                "or any reference to a specific employee. Never assume a named person works "
                "here — verify against this list first. Also call when the customer needs to "
                "choose who to book with."
            ),
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
            "name": "search_knowledge_base",
            "description": (
                "Search the business's own knowledge base (FAQ, price list, policies, "
                "after-care instructions, location/parking info, custom notes uploaded by "
                "the owner). Use this whenever the customer asks a factual question that is "
                "NOT about appointment availability — e.g. 'do you take walk-ins?', "
                "'what's your refund policy?', 'how do I prepare for the session?', "
                "'where exactly are you located?'. Returns the most relevant passages. "
                "ALWAYS prefer answering from these passages over guessing. If the search "
                "returns no results, tell the customer you don't have that information and "
                "suggest they contact the business directly."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The customer's question rephrased as a concise search query.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

# ── Reservation tools (restaurant sector) ───────────────────────────────────

RESERVATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_shifts",
            "description": "Get the list of available dining shifts (e.g. Öğle, Akşam) and restaurant reservation settings.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_table_availability",
            "description": (
                "Check if a table is available for a given date, shift, and party size. "
                "Returns the best-fit table if available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "shift_name": {"type": "string", "description": "Shift name e.g. 'Öğle' or 'Akşam'"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                },
                "required": ["date", "shift_name", "party_size"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create a table reservation after collecting all required information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {"type": "string", "description": "Full name of the guest"},
                    "customer_phone": {"type": "string", "description": "Phone number of the guest"},
                    "customer_email": {"type": "string", "description": "Email (optional)"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "shift_name": {"type": "string", "description": "Shift name e.g. 'Akşam'"},
                    "special_requests": {"type": "string", "description": "Special requests (optional)"},
                },
                "required": ["customer_name", "customer_phone", "party_size", "date", "shift_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_reservation",
            "description": "Cancel an existing reservation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "string", "description": "Reservation ID"},
                    "customer_phone": {"type": "string", "description": "Guest phone for verification"},
                },
                "required": ["reservation_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the restaurant's knowledge base for menu, policies, or other information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
]


# ── Main AI service ──────────────────────────────────────────────────────────

class AIService:
    def __init__(self, business: Business, tool_executor, kb_search=None, business_facts: str = "", customer_memory: str = ""):
        """
        Args:
            business: the Business document.
            tool_executor: async callable (fn_name, fn_args, conversation) -> dict
                that runs the AI's tool calls.
            kb_search: optional async callable (query: str) -> list[dict] that
                returns retrieval hits for pre-injection on every user turn.
            business_facts: a pre-rendered "ground-truth" block (from
                knowledge_service.build_business_facts) appended to the system
                prompt so the assistant always has authoritative info.
            customer_memory: optional block from customer_service.format_memory_block
                injected when a returning customer is recognized.
        """
        self.business = business
        self.tool_executor = tool_executor
        self.kb_search = kb_search
        self.business_facts = business_facts
        self.customer_memory = customer_memory

    def _build_system_prompt(self, language: str) -> str:
        sector = self.business.sector
        lang_key = language if language in ("tr", "en", "ru", "de", "ar") else "tr"

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

        # Returning customer context — the actual memory block (if any) is
        # appended later via `customer_memory`. This is just a generic hint
        # for cases where no Customer record exists yet.
        base_prompt += (
            "\n\nTEKRAR MÜŞTERI: Aşağıda 'TEKRAR MÜŞTERİ TANIMLANDI' bloğu varsa, "
            "müşteri sistemde kayıtlı demektir — isim/telefon tekrar SORMA, doğrudan adıyla karşıla. "
            "Blok yoksa standart akış: önce ad ve telefon iste."
        )

        # Staff selection context (async staff check happens at runtime via get_staff_list tool)
        base_prompt += (
            "\n\nPERSONEL SEÇİMİ: Eğer işletmenin birden fazla çalışanı varsa, "
            "müşteri randevu almak istediğinde `get_staff_list` aracını çağırarak aktif personelleri listele. "
            "Personel listesi boş değilse müşteriye hangi personelle randevu almak istediğini sor. "
            "Müşteri tercih belirtmezse 'herhangi biri' seçeneğini sun ve staff_id olmadan randevu oluştur. "
            "Personel seçildikten sonra `check_availability` aracını o personelin staff_id'si ile çağır."
        )

        # Knowledge base (RAG) instruction — STRICT grounding rules
        base_prompt += (
            "\n\n=== KESİN BİLGİ DOĞRULUĞU / ANTI-HALÜSİNASYON KURALLARI ===\n"
            "Bu asistan sadece bu işletmenin resmi temsilcisidir; bir 'web sitesi danışmanı' "
            "gibi davranır. Aşağıdaki kurallara KESİNLİKLE uy:\n"
            "1) Bir bilgi vermeden önce kendine sor: 'Bu bilgi (a) İŞLETME GERÇEKLERİ "
            "bloğunda mı? (b) İLGİLİ BİLGİ BANKASI PASAJLARI bloğunda mı? (c) Konuşmada "
            "müşteri kendi söyledi mi?' Üçü de hayır ise UYDURMA.\n"
            "2) KB'de olmayan bir bilgi için 'Bu konuda elimde kesin bilgi yok, "
            "işletmeyle iletişime geçmenizi öneririm' de. Tahmin, varsayım, 'genelde böyledir' "
            "tarzı cevap YASAK.\n"
            "3) Fiyat, süre, garanti, prosedür, sağlık iddiası, malzeme/marka, lokasyon "
            "detayı, çalışma günü gibi kritik bilgilerde KAYNAK GÖSTER (örn. 'SSS belgemize göre…' "
            "veya 'fiyat listemize göre…'). Bu kaynaklar mevcut bloklardaki başlıklardır.\n"
            "4) Kapsam: SADECE bu işletme hakkında konuş. Genel dünya bilgisi, rakip işletme, "
            "tıbbi/hukuki/finansal tavsiye verme. Konu dışı sorulara kibarca 'Ben sadece "
            "{business_name} hakkında yardımcı olabiliyorum' diye yönlendir.\n"
            "5) Eğer ek bilgi gerekiyorsa `search_knowledge_base` aracını farklı bir sorgu ile "
            "tekrar çağırabilirsin. Pre-injected pasajlar yeterliyse tekrar arama yapma.\n"
            "6) Cevabını VERİLEN BİLGİYE DAYANDIR; dolgu cümle veya genel geçer yorum ekleme.\n"
            "7) PERSONEL ADI KURALI: Müşteri mesajında bir kişi adı geçiyorsa (örn. 'Dr. X', "
            "'Ayşe hanım', 'Bay Y') veya belirli bir çalışana atıfta bulunuyorsa, CEVAP VERMEDEN "
            "ÖNCE mutlaka `get_staff_list` aracını çağır. Dönen listede o kişi YOKSA, "
            "varlığını ima eden ('müsaitlik kontrol edeyim', 'hangi bölümde' gibi) hiçbir cümle "
            "kurma — bunun yerine net şekilde 'Bu isimde kayıtlı bir personelimiz bulunmuyor. "
            "Doğru ismi paylaşır mısınız ya da personel listemizden tercih etmek ister misiniz?' "
            "de ve mevcut personeli listele. Asla isim üzerinden bilgi uydurma."
        ).replace("{business_name}", self.business.name)

        # Append the authoritative business facts (ground truth)
        if self.business_facts:
            base_prompt += "\n\n" + self.business_facts

        # Append per-customer memory (returning customer)
        if self.customer_memory:
            base_prompt += "\n\n" + self.customer_memory

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

        # ── Pre-retrieval: always try to ground this turn in real KB content
        retrieved_block = ""
        if self.kb_search and user_message and len(user_message.strip()) >= 4:
            try:
                hits = await self.kb_search(user_message)
                if hits:
                    from app.services.knowledge_service import format_retrieved_context
                    retrieved_block = format_retrieved_context(hits)
            except Exception:
                # Retrieval must never break the chat
                retrieved_block = ""

        # Build messages for OpenAI
        system_prompt = self._build_system_prompt(language)
        if retrieved_block:
            system_prompt += "\n\n" + retrieved_block
        messages = [{"role": "system", "content": system_prompt}]
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
        tools = RESERVATION_TOOLS if self.business.sector == "restaurant" else APPOINTMENT_TOOLS
        while True:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.3,
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
