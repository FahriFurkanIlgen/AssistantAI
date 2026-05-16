"""
Aris Antalya VIP (Aris Ezgi Doğan Antalya) — demo seed.

  - Instagram : https://www.instagram.com/arisantalyavip  (55.9K takipçi, verified)
  - Erkeklere özel şube: @arisantalyamenvip
  - Adres    : Fener Mah. Bülent Ecevit Bulvarı (Bulvar Lara) No:43/D, Antalya 07160
  - Telefon  : 0 543 242 86 00
  - WhatsApp : +90 543 242 86 66  (wa.me/905432428666)
  - Sektör   : beauty
  - Öne çıkan: "Türkiye'nin En Büyük Güzellik Merkezi"

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_aris_antalya_vip

Mevcut kayıt varsa günceller (idempotent).
"""

import asyncio
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.business import (
    Business,
    ServiceItem,
    WorkingHours,
    WorkingSchedule,
)
from app.models.staff_member import StaffMember
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.conversation import Conversation
from app.models.otp_code import OtpCode
from app.core.security import hash_password


DEMO = {
    "name": "Aris Antalya VIP — Ezgi Doğan",
    "slug": "aris-antalya-vip",
    "email": "demo@arisantalyavip.com",
    "password": "demo123456",
    "sector": "beauty",
    "phone": "0 543 242 86 00",
    "address": "Fener Mah. Bülent Ecevit Bulvarı (Bulvar Lara) No:43/D Lara / ANTALYA",
    "city": "Antalya",
    "instagram_handle": "arisantalyavip",
    "ai_persona_name": "Aris Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, Aris Antalya VIP'e hoş geldiniz. Ben Aris Asistan. "
        "Türkiye'nin kurumsal en güvenilir güzellik merkezi olarak lazer epilasyon, "
        "bölgesel incelme, gıdı eritme, cilt protokolleri, kalıcı makyaj ve daha fazlası "
        "hakkında bilgi verebilir, ücretsiz analiz randevusu oluşturabilirim. "
        "Size nasıl yardımcı olabilirim? ✨"
    ),
    "ai_welcome_message_en": (
        "Hello, welcome to Aris Antalya VIP — Ezgi Doğan. I'm Aris Assistant. "
        "As Turkey's most trusted beauty center we offer laser hair removal, body slimming, "
        "double-chin dissolving, skin protocols, permanent makeup and more. "
        "I can provide information and schedule a free analysis appointment. "
        "How may I help you? ✨"
    ),
    "ai_welcome_message_ru": (
        "Здравствуйте, добро пожаловать в Aris Antalya VIP — Ezgi Doğan. Я Aris Ассистент. "
        "Мы — ведущий корпоративный центр красоты Турции: лазерная эпиляция, коррекция фигуры, "
        "растворение второго подбородка, уходовые протоколы, перманентный макияж и многое другое. "
        "Могу рассказать подробнее и записать на бесплатный анализ. Чем могу помочь? ✨"
    ),
    "ai_welcome_message_de": (
        "Hallo, willkommen bei Aris Antalya VIP — Ezgi Doğan. Ich bin Aris Assistent. "
        "Als eines der renommiertesten Schönheitszentren der Türkei bieten wir "
        "Laser-Haarentfernung, Körperformung, Kinnfettauflösung, Hautpflegeprotokolle, "
        "Permanent-Make-up und vieles mehr. Ich kann Sie informieren und einen kostenlosen "
        "Analysetermin vereinbaren. Wie kann ich Ihnen helfen? ✨"
    ),
    "default_appointment_duration": 30,
}


# Merkez kamuya açık fiyat vermediği için ("DM üzerinden fiyat vermiyoruz" politikası)
# fiyatlar sıfır (0) bırakılmıştır; AI konsültasyon yönlendirmesi yapacaktır.
SERVICES: list[ServiceItem] = [
    # ── Lazer Epilasyon ────────────────────────────────────────────────────────
    ServiceItem(
        name="Laser Epilation — Single Zone",
        name_tr="Lazer Epilasyon — Tek Bölge",
        duration_minutes=20,
        price=0,
        description=(
            "Diode lazer ile kalıcı tüy azaltma. Seans sayısı cilt tipine göre belirlenir. "
            "Fiyat için ücretsiz analiz randevusu alın."
        ),
    ),
    ServiceItem(
        name="Laser Epilation — Full Body Package",
        name_tr="Lazer Epilasyon — Tüm Vücut Paketi",
        duration_minutes=90,
        price=0,
        description=(
            "Tüm vücut çok seanslı paket. SağlıkSen üyelerine %20 indirim uygulanır. "
            "Fiyat için ücretsiz analiz randevusu alın."
        ),
    ),

    # ── Bölgesel İncelme ──────────────────────────────────────────────────────
    ServiceItem(
        name="Body Slimming — Regional",
        name_tr="Bölgesel İncelme",
        duration_minutes=60,
        price=0,
        description=(
            "Vacu Activ, RF veya ultrason kavitasyon destekli bölgesel yağ yakma ve sıkılaştırma. "
            "Ücretsiz analiz ile kişisel program oluşturulur."
        ),
    ),
    ServiceItem(
        name="Vacu Activ Body Treatment",
        name_tr="Vacu Activ",
        duration_minutes=45,
        price=0,
        description=(
            "Vakum destekli bölgesel incelme ve selülit azaltma cihazı. "
            "Kombine paket programlarında kullanılır."
        ),
    ),

    # ── Gıdı Eritme (Double Chin) ─────────────────────────────────────────────
    ServiceItem(
        name="Double Chin Dissolving (Kybella / Mesotherapy)",
        name_tr="Gıdı Eritme",
        duration_minutes=30,
        price=0,
        description=(
            "Çene altı yağ birikimini (gıdı) eritmek için enjeksiyon veya ultrason destekli uygulama. "
            "Ücretsiz analiz ve konsültasyon gereklidir."
        ),
    ),

    # ── Cilt Bakım Protokolleri ───────────────────────────────────────────────
    ServiceItem(
        name="Aqua Peel",
        name_tr="Aqua Peel",
        duration_minutes=60,
        price=0,
        description=(
            "Hydra dermabrazyon ile gözenek temizleme, soyma ve nem infüzyonu. "
            "Parlaklık ve nem için."
        ),
    ),
    ServiceItem(
        name="Truva Peel",
        name_tr="Truva Peel",
        duration_minutes=60,
        price=0,
        description=(
            "Özel formüllü kimyasal peeling protokolü; leke ve kırışıklık azaltma, "
            "cilt tonu eşitleme."
        ),
    ),
    ServiceItem(
        name="Caviar Protocol (Havyar Protokolü)",
        name_tr="Havyar Protokolü",
        duration_minutes=75,
        price=0,
        description=(
            "Havyar özlü besleyici ve gençleştirici cilt bakım protokolü. "
            "Anti-aging ve parlaklık."
        ),
    ),
    ServiceItem(
        name="Signature Protocol (İmza Protokolü)",
        name_tr="İmza Protokolü",
        duration_minutes=90,
        price=0,
        description=(
            "Aris Antalya VIP'in özel imzalı cilt protokolü; kişiye özel adımlarla "
            "derin yenileme ve sıkılaştırma."
        ),
    ),
    ServiceItem(
        name="Spot Treatment Protocol (Leke Protokolü)",
        name_tr="Leke Protokolü",
        duration_minutes=60,
        price=0,
        description=(
            "Güneş lekesi, melazma ve post-akne lekelere yönelik kombine aydınlatma protokolü."
        ),
    ),
    ServiceItem(
        name="Hydrafacial",
        name_tr="Hydrafacial",
        duration_minutes=75,
        price=0,
        description=(
            "Medikal grade vakum + serum infüzyon sistemi ile derin temizlik, nem ve parlaklık."
        ),
    ),
    ServiceItem(
        name="Holiday Glow (Bayram Işıltısı)",
        name_tr="Bayram Işıltısı",
        duration_minutes=60,
        price=0,
        description=(
            "Özel gün / bayram öncesi hızlı parlaklık ve cilt tonu eşitleme paketi."
        ),
    ),

    # ── Kolajen & Dolgunlaştırma ──────────────────────────────────────────────
    ServiceItem(
        name="Thread Collagen (Kolajen İp)",
        name_tr="Kolajen İp",
        duration_minutes=60,
        price=0,
        description=(
            "Absorbable PDO veya PCL ip ile cilt germe ve kolajen sentezi uyarımı."
        ),
    ),

    # ── Kalıcı Makyaj ─────────────────────────────────────────────────────────
    ServiceItem(
        name="Microblading — Eyebrows",
        name_tr="Microblading — Kaş",
        duration_minutes=120,
        price=0,
        description=(
            "El tekniği microblading veya ombre/powder brow. Touch-up seans dahil. "
            "Ücretsiz konsültasyon ile renk ve şekil planlaması yapılır."
        ),
    ),
    ServiceItem(
        name="Permanent Makeup — Lips",
        name_tr="Kalıcı Makyaj — Dudak",
        duration_minutes=120,
        price=0,
        description=(
            "Aquarelle veya ombre dudak pigmentasyonu. Touch-up dahil."
        ),
    ),
    ServiceItem(
        name="Permanent Makeup — Eyeliner",
        name_tr="Kalıcı Makyaj — Eyeliner",
        duration_minutes=90,
        price=0,
        description=(
            "Üst/alt hat kalıcı eyeliner. Touch-up dahil."
        ),
    ),

    # ── Tırnak ────────────────────────────────────────────────────────────────
    ServiceItem(
        name="Nail Prosthetics (Protez Tırnak)",
        name_tr="Protez Tırnak",
        duration_minutes=90,
        price=0,
        description="Jel veya akrilik protez tırnak uygulaması; nail art seçenekleriyle.",
    ),

    # ── Ücretsiz Analiz ───────────────────────────────────────────────────────
    ServiceItem(
        name="Free Skin & Body Analysis Consultation",
        name_tr="Ücretsiz Cilt & Vücut Analiz Konsültasyonu",
        duration_minutes=30,
        price=0,
        description=(
            "Tüm hizmetler öncesinde yapılan ücretsiz yüz yüze analiz. "
            "Uzman ekip kişisel program önerir."
        ),
    ),
]


SCHEDULE = WorkingSchedule(
    monday=WorkingHours(start="09:00", end="21:00", is_open=True),
    tuesday=WorkingHours(start="09:00", end="21:00", is_open=True),
    wednesday=WorkingHours(start="09:00", end="21:00", is_open=True),
    thursday=WorkingHours(start="09:00", end="21:00", is_open=True),
    friday=WorkingHours(start="09:00", end="21:00", is_open=True),
    saturday=WorkingHours(start="09:00", end="20:00", is_open=True),
    sunday=WorkingHours(start="10:00", end="18:00", is_open=True),
)


CUSTOM_AI_INSTRUCTIONS = """
SEN KİMSİN
- Sen Aris Antalya VIP — Ezgi Doğan'ın resmi dijital asistanı "Aris Asistan"sın.
- Görevin: müşterilere hizmetler, prosedürler, çalışma saatleri, kampanyalar ve ücretsiz
  analiz randevusu hakkında samimi ve güven veren bilgi vermek; randevu oluşturmak.
- Tıbbi teşhis veya medikal tavsiye verme; "Uzman ekibimiz ücretsiz analizde size özel
  program oluşturacaktır" şeklinde yönlendir.

KURUM BİLGİLERİ
- Resmi ad      : Aris Antalya VIP — Aris Ezgi Doğan Antalya 3E
- Slogan        : "Türkiye'nin En Büyük Güzellik Merkezi" /
                  "Türkiye'nin Kurumsal En Güvenilir Güzellik Merkezi"
- Adres         : Fener Mah. Bülent Ecevit Bulvarı (Bulvar Lara) No:43/D Lara / ANTALYA 07160
- Telefon       : 0 543 242 86 00
- WhatsApp      : +90 543 242 86 66  (wa.me/905432428666)
- Instagram     : @arisantalyavip  (55.9K takipçi, doğrulanmış hesap)
- Erkeklere özel şube: @arisantalyamenvip
- SağlıkSen üyeleri için kadın ve erkek bölümlerinde %20 indirim geçerlidir.
- Merkez yaklaşık 5 yıldır (2021 kuruluş) hizmet vermektedir; "5. Yıl Kampanyası" aktif.
- Ramazan ve bayram dönemlerinde özel kampanyalar yürütülmektedir.

ÇALIŞMA SAATLERİ
- Pazartesi–Cuma : 09:00–21:00
- Cumartesi      : 09:00–20:00
- Pazar          : 10:00–18:00

FİYAT POLİTİKASI
- Merkez kamuya açık fiyat listesi paylaşmamaktadır ("DM üzerinden fiyat vermiyoruz" politikası).
- Fiyatlar kişisel analiz sonucunda belirlenir; ücretsiz analiz randevusu al.
- SağlıkSen üyeleri: tüm hizmetlerde %20 indirim.
- Kampanya dönemlerinde (Anneler Günü, 8 Mart, Bayram, Ramazan) özel fırsatlar.
- "Fiyat nedir?" sorusuna şöyle yanıt ver: "Fiyatlarımız kişisel cilt/vücut analizinize göre
  oluşturulur. Size en uygun programı belirlemek için ücretsiz analiz randevusu ayarlayalım."

HİZMET KATALOĞU (özet)

LAZ. EPİLASYON
- Tek bölge veya tüm vücut paket; diode lazer.
- Seans arası 4–6 hafta; ortalama 6–10 seans.
- SağlıkSen üyelerine %20 indirim.
- Sonuç alamama sebepleri: hormon, yanlış seans aralığı, cihaz kalitesi (bizde medikal sınıf cihaz kullanılır).

BÖLGESEL İNCELME
- Vacu Activ, RF, ultrason kavitasyon veya kombine protokol.
- Teknoloji seçimi ücretsiz analizde belirlenir.
- "Doğru teknoloji ile istenen incelme" yaklaşımı.

GIDI ERİTME
- Çene altı yağ birikimini enjeksiyon veya ultrason ile eritme.
- 1–3 seans; ücretsiz konsültasyon zorunlu.

CİLT BAKIM PROTOKOLLERI
- Aqua Peel      : gözenek temizleme, hydrasyon
- Truva Peel     : leke, kırışık, ton eşitleme
- Havyar Protokolü: beslenme, anti-aging
- İmza Protokolü : kişiye özel derin yenileme (Aris'in imza uygulaması)
- Leke Protokolü : güneş lekesi, melazma, post-akne
- Hydrafacial    : medikal grad derin temizlik
- Bayram Işıltısı: özel gün hızlı parlaklık paketi
- Cilt Protokolü : kapsamlı bireysel bakım programı

KOLAJEN İP
- PDO/PCL ip ile yüz, boyun ve vücut sıkılaştırma.
- Kolajen sentezi uyarımı; 6–18 ay etkisi sürer.

KALICI MAKYAJ
- Microblading / Ombre Brow (kaş)
- Aquarelle / Ombre Dudak
- Eyeliner
- Touch-up seans dahildir.

PROTEZ TIRNAK
- Jel veya akrilik; nail art seçenekleriyle.

ÜCRETSİZ ANALİZ
- Tüm hizmetler öncesinde ücretsiz yüz yüze analiz.
- "Müşteri memnuniyeti" en önemli öncelik — memnuniyet referansları Instagram'da bol.

RANDEVU SÜRECİ
- Randevu için: ad-soyad, hangi hizmet (veya "ne istediğini bilmiyorum — analiz istiyorum"),
  tercih tarih ve saat al.
- Kullanıcı hangi hizmeti istediğinden emin değilse "Ücretsiz analiz randevusu" öner.
- Randevu onayını özet olarak tekrar et: hizmet, tarih, saat, telefon (0 543 242 86 00).
- Erkek müşterileri erkeklere özel şubeye (@arisantalyamenvip) yönlendir;
  randevu bu asistan üzerinden de oluşturulabilir.

YANIT KURALLARI
- Türkçe konuşana Türkçe, İngilizce konuşana İngilizce, Rusça konuşana Rusça,
  Almanca konuşana Almanca yanıt ver.
- Samimi, güven veren, profesyonel ama sıcak bir ton kullan.
- "Türkiye'nin en güvenilir güzellik merkezi" kimliğini yansıt; kalite ve uzmanlığı vurgula.
- Fiyat baskısı yaparsa: "Fiyatlarımız kişisel analize göre şekillenir; sizi karşılayacak
  en uygun programı ücretsiz analizde sunalım."
""".strip()


async def main() -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Business,
            StaffMember,
            Customer,
            Appointment,
            Conversation,
            OtpCode,
        ],
    )

    existing = await Business.find_one(Business.slug == DEMO["slug"])
    now = datetime.utcnow()

    if existing:
        print(f"↺ Mevcut kayıt bulundu, güncelleniyor: {existing.email}")
        existing.name = DEMO["name"]
        existing.email = DEMO["email"]
        existing.hashed_password = hash_password(DEMO["password"])
        existing.sector = DEMO["sector"]
        existing.phone = DEMO["phone"]
        existing.address = DEMO["address"]
        existing.city = DEMO["city"]
        existing.instagram_handle = DEMO["instagram_handle"]
        existing.ai_persona_name = DEMO["ai_persona_name"]
        existing.ai_welcome_message_tr = DEMO["ai_welcome_message_tr"]
        existing.ai_welcome_message_en = DEMO["ai_welcome_message_en"]
        existing.ai_welcome_message_ru = DEMO["ai_welcome_message_ru"]
        existing.ai_welcome_message_de = DEMO["ai_welcome_message_de"]
        existing.custom_ai_instructions = CUSTOM_AI_INSTRUCTIONS
        existing.default_appointment_duration = DEMO["default_appointment_duration"]
        existing.services = SERVICES
        existing.working_schedule = SCHEDULE
        existing.is_active = True
        existing.updated_at = now
        await existing.save()
        biz = existing
    else:
        print(f"＋ Yeni demo kuruluş oluşturuluyor: {DEMO['email']}")
        biz = Business(
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
            ai_welcome_message_tr=DEMO["ai_welcome_message_tr"],
            ai_welcome_message_en=DEMO["ai_welcome_message_en"],
            ai_welcome_message_ru=DEMO["ai_welcome_message_ru"],
            ai_welcome_message_de=DEMO["ai_welcome_message_de"],
            custom_ai_instructions=CUSTOM_AI_INSTRUCTIONS,
            default_appointment_duration=DEMO["default_appointment_duration"],
            services=SERVICES,
            working_schedule=SCHEDULE,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        await biz.insert()

    print("─" * 60)
    print(f"✓ Hazır: {biz.name}")
    print(f"  ID          : {biz.id}")
    print(f"  Slug        : {biz.slug}")
    print(f"  E-posta     : {biz.email}")
    print(f"  Şifre       : {DEMO['password']}")
    print(f"  Servis sayısı: {len(biz.services)}")
    print(f"  Chat URL    : http://localhost:3000/chat/{biz.slug}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
