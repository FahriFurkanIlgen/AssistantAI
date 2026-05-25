"""
Seraser Fine Dining Restaurant — demo seed (restaurant sector).

  - Web           : http://seraserrestaurant.com
  - Instagram     : https://www.instagram.com/seraser.restaurant/
  - WhatsApp      : +90 546 847 60 15
  - Telefon       : +90 242 247 60 15
  - Adres         : Tuzcular Mah. Karanlık Sok. No:18 Kaleiçi, 07100 Antalya
  - Sektör        : restaurant
  - Slug          : seraser-restaurant
  - E-posta       : demo@seraserrestaurant.com
  - Şifre         : demo123456
  - Konsept       : Fine dining — Uluslararası mutfak, 300 yıllık konak, Kaleiçi
  - Masalar       : 14 masa (iç mekan, teras, VIP)
  - Vardiyalar    : Öğle (12:00–16:00) ve Akşam (19:00–23:00)
  - Diller        : TR, EN, DE, RU

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_restaurant_demo

Mevcut kayıt varsa günceller (idempotent).
"""

import asyncio
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.business import (
    Business,
    ServiceItem,
    WorkingHours,
    WorkingSchedule,
    RestaurantConfig,
    RestaurantTable,
    DiningShift,
)
from app.models.staff_member import StaffMember
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.conversation import Conversation
from app.models.otp_code import OtpCode
from app.models.reservation import Reservation
from app.core.security import hash_password

DEMO = {
    "name": "Seraser Fine Dining Restaurant",
    "slug": "seraser-restaurant",
    "email": "demo@seraserrestaurant.com",
    "password": "demo123456",
    "sector": "restaurant",
    "phone": "+90 242 247 60 15",
    "address": "Tuzcular Mah. Karanlık Sok. No:18 Kaleiçi, 07100 Antalya",
    "city": "Antalya",
    "instagram_handle": "seraser.restaurant",
    "ai_persona_name": "Seraser",
    "ai_welcome_message_tr": (
        "Merhaba, Seraser Fine Dining'e hoş geldiniz. "
        "Antalya'nın kalbinde, 300 yıllık bir konakta uluslararası ve geleneksel "
        "lezzetleri bir araya getiriyoruz. "
        "Masa rezervasyonu için tarih, kişi sayısı ve bölüm tercihinizi paylaşın, "
        "sizin için en uygun masayı ayarlayayım. ✨"
    ),
    "ai_welcome_message_en": (
        "Welcome to Seraser Fine Dining Restaurant. "
        "Nestled in a 300-year-old mansion in Kaleiçi, Antalya, we blend international "
        "cuisine with traditional motifs. "
        "To reserve a table, please share your preferred date, party size and section — "
        "I'll take care of the rest. ✨"
    ),
    "ai_welcome_message_de": (
        "Willkommen im Seraser Fine Dining Restaurant. "
        "In einem 300 Jahre alten Herrenhaus im Herzen von Antalya verbinden wir "
        "internationale Küche mit traditionellen Motiven. "
        "Für eine Tischreservierung teilen Sie uns bitte Datum, Personenanzahl und "
        "gewünschten Bereich mit. ✨"
    ),
    "ai_welcome_message_ru": (
        "Добро пожаловать в ресторан Seraser Fine Dining. "
        "В особняке возрастом 300 лет в сердце Калеичи мы сочетаем международную кухню "
        "с традиционными мотивами. "
        "Чтобы забронировать столик, укажите дату, количество гостей и предпочтительный "
        "зал. ✨"
    ),
    "custom_ai_instructions": """\
Seraser Fine Dining Restaurant, Antalya Kaleiçi'nde 300 yıllık tarihi bir konakta
hizmet veren ödüllü bir fine dining restoranıdır. 2009'dan bu yana uluslararası
mutfağı geleneksel motiflerle harmanlıyoruz.

MENÜ KATEGORİLERİ & ÖNE ÇIKANLAR:

Başlangıçlar (Starters):
• Goat Cheese & Aubergine Souffle – 700 TL
• Moules Mariniere (Fransız usulü midye) – 850 TL
• Beef Carpaccio (roka, trüf yağı) – 995 TL
• Grilled Jumbo Shrimps & Aegean Herbs Cream – 2050 TL
• Foie Gras (ördek ciğeri, kan portakalı reçeli) – 2450 TL
• Seabass Ceviche – 1100 TL

Makarna & Risotto (Pastas):
• Seafood Black Fettucine (karides, kalamar, midye) – 995 TL
• Risotto with Porcini Mushrooms – 850 TL
• Octopus Carpaccio & Risotto – 995 TL

Sushi:
• Hot Tempura Seraser Roll – 850 TL
• Rainbow Roll – 850 TL
• Mix Sushi Plate (25 parça) – 2850 TL

Ana Yemekler (Mains):
• Lamb Cotlet (kuzu pirzola, badem kaplı patates) – 1750 TL
• Char Grilled Rib Steak (28 gün dry-aged) – 1600 TL
• Beef Wellington – 1850 TL
• Bonfser (fileto, porcini mantarı, graten patates) – 1950 TL
• Sea Bass Wrapped in Vine Leaves – 1300 TL
• Roasted Mediterranean Grouper – 2750 TL
• Mediterranean Pearl (ıstakoz, jumbo karides, ahtapot) – 2950 TL
• Kebab-ı Seraser (dana kuyruk, gorgonzola sos) – 1450 TL

Tatlılar (Desserts):
• Modern Baklava (Antep fıstıklı dondurma ile) – 500 TL
• Dilly's Legendary Chocolate Truffle (şekersiz, unsuz) – 500 TL
• Sultan's Coffee (Türk kahvesi aromalı crème brûlée) – 500 TL
• Palace's Lokma (trüf çikolata, tarçın şekeri) – 500 TL

BÖLÜMLER:
• İç Mekan (Indoor): 8 masa, tarihi konak atmosferi, yıl boyu açık
• Teras (Terrace): 4 masa, tarihi Kaleiçi manzarası, bahar-yaz-sonbahar
• VIP Salon: 2 özel masa (V1–V2), özel etkinlik ve romantik akşam yemekleri için

ÇALIŞMA SAATLERİ:
• Her gün: 12:00 – 00:00
• Mutfak kapanış: 23:00

REZERVASYON KURALLARI:
- Müşteriden ad, telefon ve kişi sayısı mutlaka alınmalı
- VIP masalar için minimum 2 kişi; özel etkinlikler için önceden bildirim gerekli
- Teras masaları Kasım–Mart arası kapalıdır; uyarı ver
- Doğum günü, yıl dönümü gibi özel notları kaydet; "surprise dessert" önerebilirsin
- Rezervasyon onayı için +90 242 247 60 15 numarası veya WhatsApp: +90 546 847 60 15

GENEL BİLGİ:
- Ücretsiz vale park
- Canlı piyano / vokal performans (seçili gecelerde)
- Dress code: Smart casual ve üzeri önerilir
- Tam lisanslı; geniş dünya şarabı listesi mevcut
- Kurumsal yemek ve özel organizasyon için reservations@seraserrestaurant.com
""",
}

TABLES: list[dict] = [
    # İç Mekan
    {"number": "1",  "name": "Pencere 1",    "capacity": 2, "section": "iç",    "shape": "rect",  "x": 5.0,  "y": 5.0},
    {"number": "2",  "name": "Pencere 2",    "capacity": 2, "section": "iç",    "shape": "rect",  "x": 5.0,  "y": 20.0},
    {"number": "3",  "name": "Merkez 1",     "capacity": 4, "section": "iç",    "shape": "rect",  "x": 18.0, "y": 5.0},
    {"number": "4",  "name": "Merkez 2",     "capacity": 4, "section": "iç",    "shape": "rect",  "x": 18.0, "y": 20.0},
    {"number": "5",  "name": "Merkez 3",     "capacity": 4, "section": "iç",    "shape": "rect",  "x": 18.0, "y": 36.0},
    {"number": "6",  "name": "Köşe 1",       "capacity": 6, "section": "iç",    "shape": "rect",  "x": 32.0, "y": 5.0},
    {"number": "7",  "name": "Köşe 2",       "capacity": 6, "section": "iç",    "shape": "rect",  "x": 32.0, "y": 22.0},
    {"number": "8",  "name": "Büyük Salon",  "capacity": 8, "section": "iç",    "shape": "rect",  "x": 32.0, "y": 42.0},
    # Teras
    {"number": "9",  "name": "Teras 1",      "capacity": 2, "section": "teras", "shape": "round", "x": 55.0, "y": 8.0},
    {"number": "10", "name": "Teras 2",      "capacity": 4, "section": "teras", "shape": "round", "x": 65.0, "y": 8.0},
    {"number": "11", "name": "Teras 3",      "capacity": 4, "section": "teras", "shape": "round", "x": 55.0, "y": 26.0},
    {"number": "12", "name": "Teras 4",      "capacity": 6, "section": "teras", "shape": "rect",  "x": 65.0, "y": 26.0},
    # VIP
    {"number": "V1", "name": "VIP Salon A",  "capacity": 6, "section": "vip",   "shape": "rect",  "x": 80.0, "y": 10.0},
    {"number": "V2", "name": "VIP Salon B",  "capacity": 10,"section": "vip",   "shape": "rect",  "x": 80.0, "y": 38.0},
]

SHIFTS: list[dict] = [
    {
        "name": "Öğle",
        "start_time": "12:00",
        "end_time": "16:00",
        "is_active": True,
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    },
    {
        "name": "Akşam",
        "start_time": "19:00",
        "end_time": "23:00",
        "is_active": True,
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    },
]


async def main() -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Business, StaffMember, Customer, Appointment,
            Conversation, OtpCode, Reservation,
        ],
    )

    existing = await Business.find_one(Business.slug == DEMO["slug"])

    # Build tables and shifts
    tables = [
        RestaurantTable(
            id=str(uuid.uuid4()),
            number=t["number"],
            name=t.get("name"),
            capacity=t["capacity"],
            section=t["section"],
            shape=t["shape"],
            is_active=True,
            x=t["x"],
            y=t["y"],
        )
        for t in TABLES
    ]
    shifts = [
        DiningShift(
            id=str(uuid.uuid4()),
            name=s["name"],
            start_time=s["start_time"],
            end_time=s["end_time"],
            is_active=s["is_active"],
            days=s["days"],
        )
        for s in SHIFTS
    ]

    restaurant_cfg = RestaurantConfig(
        enabled=True,
        tables=tables,
        shifts=shifts,
        reservation_duration=120,
        max_party_size=10,
        reservation_window_days=60,
    )

    schedule = WorkingSchedule(
        monday=WorkingHours(start="12:00", end="00:00"),
        tuesday=WorkingHours(start="12:00", end="00:00"),
        wednesday=WorkingHours(start="12:00", end="00:00"),
        thursday=WorkingHours(start="12:00", end="00:00"),
        friday=WorkingHours(start="12:00", end="00:00"),
        saturday=WorkingHours(start="12:00", end="00:00"),
        sunday=WorkingHours(start="12:00", end="00:00"),
    )

    services = [
        ServiceItem(
            name="Table Reservation",
            name_tr="Masa Rezervasyonu",
            duration_minutes=120,
            description="Standard fine dining reservation (automatic table assignment)",
        ),
        ServiceItem(
            name="VIP Reservation",
            name_tr="VIP Masa Rezervasyonu",
            duration_minutes=180,
            description="Private VIP salon for special occasions — min 2 guests",
        ),
        ServiceItem(
            name="Corporate Dinner",
            name_tr="Kurumsal Yemek",
            duration_minutes=180,
            description="Corporate & group dining — contact for custom arrangements",
        ),
        ServiceItem(
            name="Special Occasion",
            name_tr="Özel Etkinlik",
            duration_minutes=180,
            description="Birthday, anniversary, proposal — special setup available",
        ),
    ]

    ai_welcome = {
        "tr": DEMO["ai_welcome_message_tr"],
        "en": DEMO["ai_welcome_message_en"],
        "de": DEMO["ai_welcome_message_de"],
        "ru": DEMO["ai_welcome_message_ru"],
    }

    if existing:
        existing.name = DEMO["name"]
        existing.hashed_password = hash_password(DEMO["password"])
        existing.sector = DEMO["sector"]
        existing.phone = DEMO["phone"]
        existing.address = DEMO["address"]
        existing.city = DEMO["city"]
        existing.instagram_handle = DEMO["instagram_handle"]
        existing.ai_persona_name = DEMO["ai_persona_name"]
        existing.ai_welcome_message = ai_welcome
        existing.custom_ai_instructions = DEMO["custom_ai_instructions"]
        existing.services = services
        existing.working_schedule = schedule
        existing.restaurant = restaurant_cfg
        await existing.save()
        business = existing
        print(f"[update] {business.slug}  id={business.id}")
    else:
        business = Business(
            name=DEMO["name"],
            slug=DEMO["slug"],
            email=DEMO["email"],
            hashed_password=hash_password(DEMO["password"]),
            sector=DEMO["sector"],
            phone=DEMO["phone"],
            address=DEMO["address"],
            city=DEMO["city"],
            instagram_handle=DEMO["instagram_handle"],
            ai_persona_name=DEMO["ai_persona_name"],
            ai_welcome_message=ai_welcome,
            custom_ai_instructions=DEMO["custom_ai_instructions"],
            services=services,
            working_schedule=schedule,
            restaurant=restaurant_cfg,
        )
        await business.insert()
        print(f"[insert] {business.slug}  id={business.id}")

    print(f"  Tables : {len(tables)}")
    print(f"  Shifts : {len(shifts)}")
    print(f"  Restaurant enabled: {restaurant_cfg.enabled}")
    print("Done ✓")


if __name__ == "__main__":
    asyncio.run(main())
