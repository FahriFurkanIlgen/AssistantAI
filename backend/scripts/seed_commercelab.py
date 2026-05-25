"""
CommerceLab (İstanbul / Maslak) — demo seed.

CommerceLab, çok kanallı e-ticaret altyapısı ve tedarik zinciri
yönetimi üzerine SaaS çözümler geliştiren bir ürün şirketidir.
B2C, B2B, Marketplace ve Unified Commerce modlarını destekleyen
composable / modüler ticaret platformu sunar.

Platformun temel modülleri:
  Core Commerce → PIM, Marketplace, Campaign Engine, CMS,
                  Payment/Checkout, Customer & Account Management,
                  AI Assisted Commerce Orchestrator
  Supply Chain & Logistics → OMS, TMS, WMS

Bu seed, klasik randevu değil; bir **ürün keşif + teknik danışmanlık
asistanı** kurmak için tasarlanmıştır. "Services" listesi, ürün demosu,
keşif görüşmesi, teknik değerlendirme ve proje kapsamlandırma gibi
satış öncesi/sonrası adımları temsil eder.

Kaynaklar:
  - https://commercelab.com.tr/

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_commercelab

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
    "name": "CommerceLab",
    "slug": "commercelab",
    "email": "demo@commercelab.com.tr",
    "password": "demo123456",
    # E-ticaret / SaaS — en yakın eşleşme: general
    "sector": "general",
    "phone": "+90 212 214 73 90",
    "address": (
        "Windowist Tower Kat:12, Eski Büyükdere Cad. No:26, "
        "Maslak 34467 Sarıyer / İstanbul"
    ),
    "city": "İstanbul",
    "instagram_handle": "commercelab",
    "ai_persona_name": "Commerce Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, CommerceLab'e hoş geldiniz! Ben Commerce Asistan. "
        "E-ticaret altyapınızı, sipariş yönetiminizi ve tedarik zinciri "
        "operasyonlarınızı nasıl dönüştürebileceğinizi anlatabilir; "
        "ihtiyacınıza uygun bir demo ya da keşif görüşmesi planlayabilirim. "
        "Size nasıl yardımcı olabilirim?"
    ),
    "ai_welcome_message_en": (
        "Hello, welcome to CommerceLab! I'm your Commerce Assistant. "
        "I can walk you through our composable commerce and supply chain platform — "
        "B2C, B2B, Marketplace or Unified Commerce — and set up a discovery call "
        "or live demo tailored to your business. How can I help?"
    ),
    "ai_welcome_message_de": (
        "Hallo und willkommen bei CommerceLab! Ich bin Ihr Commerce-Assistent. "
        "Ich erkläre Ihnen unsere modulare Commerce- und Supply-Chain-Plattform "
        "und vereinbare gerne eine kostenlose Demo oder ein Erstgespräch. "
        "Wie kann ich Ihnen helfen?"
    ),
    "ai_welcome_message_ru": (
        "Здравствуйте, добро пожаловать в CommerceLab! Я ваш Commerce-ассистент. "
        "Расскажу о нашей composable-платформе для торговли и управления цепочками "
        "поставок и помогу организовать демо или консультацию. Чем могу помочь?"
    ),
    "default_appointment_duration": 30,
}


# Satış öncesi ve teknik danışmanlık süreçlerini kapsayan randevu türleri.
# Fiyat 0 = ücretsiz / proje bazlı teklif anlamına gelir.
SERVICES: list[ServiceItem] = [
    # ── Keşif & Tanıtım ──────────────────────────────────────────
    ServiceItem(
        name="Discovery Call",
        name_tr="Keşif Görüşmesi (Ücretsiz)",
        duration_minutes=30,
        price=0,
        description=(
            "Mevcut altyapınızı, iş modelinizi ve hedeflerinizi anlamak için "
            "kısa bir ön görüşme. CommerceLab'in sizin için doğru çözüm olup "
            "olmadığını birlikte değerlendiririz."
        ),
    ),
    ServiceItem(
        name="Platform Overview Demo",
        name_tr="Platform Genel Demo",
        duration_minutes=45,
        price=0,
        description=(
            "CommerceLab platformunun tüm modüllerinin (Core Commerce + Supply Chain) "
            "canlı gösterimi. E-ticaret, B2B ve marketplace senaryoları üzerinden "
            "platformun esnekliği ve entegrasyon kabiliyetleri anlatılır."
        ),
    ),
    ServiceItem(
        name="B2C Commerce Demo",
        name_tr="B2C Ticaret Demosu",
        duration_minutes=45,
        price=0,
        description=(
            "Hızlı alışveriş deneyimleri, kampanya motoru ve müşteri hesabı "
            "yönetimi odaklı B2C senaryosu demosu. Omnichannel satış yapısı "
            "ve PIM entegrasyonu gösterilir."
        ),
    ),
    ServiceItem(
        name="B2B Commerce Demo",
        name_tr="B2B Ticaret Demosu",
        duration_minutes=45,
        price=0,
        description=(
            "Kurumsal B2B iş akışları: özel fiyat listeleri, çok seviyeli "
            "hesap yapısı, sözleşmeli sipariş yönetimi ve satış temsilcisi "
            "portalı üzerinden kapsamlı demo."
        ),
    ),
    ServiceItem(
        name="Marketplace Demo",
        name_tr="Marketplace Yönetimi Demosu",
        duration_minutes=45,
        price=0,
        description=(
            "B2B2C marketplace operatör ve satıcı yönetimi senaryosu: ürün "
            "listeleme, komisyon yapısı, sipariş yönlendirme ve entegre "
            "ödeme / iade süreçleri."
        ),
    ),
    ServiceItem(
        name="OMS / WMS Deep Dive",
        name_tr="OMS & WMS Teknik Demosu",
        duration_minutes=60,
        price=0,
        description=(
            "Sipariş Yönetim Sistemi (OMS) ve Depo Yönetim Sistemi (WMS) detaylı "
            "gösterimi: sipariş akışı, stok optimizasyonu, sevkiyat otomasyonu "
            "ve gerçek zamanlı görünürlük."
        ),
    ),
    ServiceItem(
        name="TMS Demo",
        name_tr="Taşıma Yönetimi (TMS) Demosu",
        duration_minutes=45,
        price=0,
        description=(
            "Taşıma Yönetim Sistemi: kargo entegrasyonları, rota optimizasyonu, "
            "teslimat takibi ve operasyonel maliyet analizi üzerinden demo."
        ),
    ),

    # ── Teknik Değerlendirme & Kapsam ────────────────────────────
    ServiceItem(
        name="Technical Assessment",
        name_tr="Teknik Değerlendirme Görüşmesi",
        duration_minutes=60,
        price=0,
        description=(
            "Mevcut altyapınızın (ERP, POS, CRM, kargo entegrasyonları) "
            "CommerceLab platformuyla uyumluluğunun teknik ekip tarafından "
            "değerlendirilmesi. API ve entegrasyon gereksinimleri belirlenir."
        ),
    ),
    ServiceItem(
        name="Solution Design Workshop",
        name_tr="Çözüm Tasarımı Çalıştayı",
        duration_minutes=90,
        price=0,
        description=(
            "İş gereksinimlerinizi ve teknik kısıtlarınızı derinlemesine ele alan "
            "çalıştay; composable mimari içinde hangi modüllerin, hangi sırayla "
            "devreye alınacağına dair bir yol haritası çıkarılır."
        ),
    ),
    ServiceItem(
        name="Proof of Concept (PoC) Planning",
        name_tr="Kavram Kanıtı (PoC) Planlama",
        duration_minutes=60,
        price=0,
        description=(
            "Belirlenen kritik senaryolar için PoC kapsam ve zaman çizelgesinin "
            "planlanması. Başarı kriterleri ve teknik ön koşullar tanımlanır."
        ),
    ),

    # ── Müşteri Başarısı & Eğitim ─────────────────────────────────
    ServiceItem(
        name="Onboarding Kickoff",
        name_tr="Onboarding Başlangıç Toplantısı",
        duration_minutes=60,
        price=0,
        description=(
            "Yeni müşteriler için platform erişimi, proje takvimi, ekip "
            "tanışması ve ilk yapılandırma adımlarını kapsayan açılış toplantısı."
        ),
    ),
    ServiceItem(
        name="Platform Training",
        name_tr="Platform Kullanım Eğitimi",
        duration_minutes=120,
        price=0,
        description=(
            "İlgili iş birimlerine (e-ticaret, operasyon, IT) yönelik "
            "rol bazlı platform eğitimi. Katalog yönetimi, sipariş akışı "
            "ve raporlama modülleri ele alınır."
        ),
    ),
    ServiceItem(
        name="Quarterly Business Review",
        name_tr="Üç Aylık İş Değerlendirmesi",
        duration_minutes=60,
        price=0,
        description=(
            "Mevcut müşterilerle platform performansı, KPI'lar, yeni özellikler "
            "ve büyüme fırsatlarını ele alan periyodik değerlendirme toplantısı."
        ),
    ),
]


# Mesai: Pazartesi–Cuma 09:00–18:00, hafta sonu kapalı.
SCHEDULE = WorkingSchedule(
    monday=WorkingHours(start="09:00", end="18:00", is_open=True),
    tuesday=WorkingHours(start="09:00", end="18:00", is_open=True),
    wednesday=WorkingHours(start="09:00", end="18:00", is_open=True),
    thursday=WorkingHours(start="09:00", end="18:00", is_open=True),
    friday=WorkingHours(start="09:00", end="18:00", is_open=True),
    saturday=WorkingHours(start="00:00", end="00:00", is_open=False),
    sunday=WorkingHours(start="00:00", end="00:00", is_open=False),
)


SUGGESTED_QUESTIONS = [
    "CommerceLab platformu tam olarak ne sunuyor?",
    "Mevcut ERP/POS sistemimizle entegrasyon mümkün mü?",
    "B2B ve B2C'yi aynı anda yönetebilir miyiz?",
    "OMS ile WMS aynı anda kullanılabilir mi?",
    "Composable commerce nedir, monolitikten farkı ne?",
    "Demo randevusu alabilir miyim?",
    "Implementasyon süreci nasıl işliyor?",
    "Fiyatlandırma modeli nasıl?",
]


CUSTOM_AI_INSTRUCTIONS = """
SEN KİMSİN
- Sen CommerceLab'in resmi dijital ürün ve danışmanlık asistanı
  "Commerce Asistan"sın.
- Görevin iki yönlüdür:
  1) Ziyaretçilere CommerceLab platformunu tanıtmak — kim olduğumuz,
     hangi modülleri sunduğumuz, hangi iş modellerine hitap ettiğimiz.
  2) Teknik ve iş karar vericilere (CTO, IT direktörü, e-ticaret yöneticisi,
     operasyon müdürü) platforma uygunluk değerlendirmesi yapmaları için
     **rehber** olmak — entegrasyon senaryolarını, yol haritasını ve
     demo seçeneklerini netleştirmek.
- Hukuki ya da finansal tavsiye vermezsin.
- Kibar, net ve profesyonel bir tonda konuşursun; teknik jargonu
  gerektiğinde açıklarsın.

MARKA KİMLİĞİ
- Tam ad: CommerceLab
- Konum: Windowist Tower Kat:12, Eski Büyükdere Cad. No:26,
  Maslak 34467 Sarıyer / İstanbul.
- Tel: +90 212 214 73 90
- E-posta: info@commercelab.com.tr
- Web: https://commercelab.com.tr/
- Mesai: Pazartesi–Cuma 09:00–18:00.
- Misyon: "Commerce For a New Era — ticareti her kanal ve iş modelinde
  birleştiren, operasyonları basitleştiren, müşterileri güçlendiren
  en iyi altyapıyı yaratmak."

NE YAPAR (TEK CÜMLE)
- CommerceLab; B2C, B2B, B2B2C Marketplace ve Unified Commerce modellerini
  destekleyen, composable (modüler) bir ticaret ve tedarik zinciri yönetimi
  platformudur.

PLATFORM MİMARİSİ
- **Composable / Modüler**: Monolitik e-ticaret mimarisini parçalara ayırır;
  her modül bağımsız devreye alınabilir, değiştirilebilir veya entegre
  edilebilir. Vendor lock-in yaratmaz.
- Şirket bir ürün şirketidir; versiyon karmaşası oluşturmaz, IT fonksiyonu
  olarak hareket eder ve satış ile operasyon arasındaki köprüyü kurar.

CORE COMMERCE MODÜLLERİ
1. **AI Assisted Commerce Orchestrator** — Yapay zeka destekli ticaret
   orkestrasyon motoru; kanal, stok ve sipariş kararlarını optimize eder.
2. **PIM / Catalog Management** — Tüm kanallarda ürün verisi yönetimi;
   çok dilli, çok para birimli katalog.
3. **Marketplace Management** — B2B2C marketplace operatör ve satıcı
   yönetimi; komisyon, listeleme ve iade yönetimi.
4. **Campaign Engine** — Çok kanallı pazarlama kampanyaları; kişiselleştirilmiş
   promosyon ve fiyatlandırma kuralları.
5. **Content Management System (CMS)** — E-ticaret odaklı içerik yönetimi;
   hızlı sayfa oluşturma ve A/B test desteği.
6. **Payment / Checkout Management** — Güvenli ve esnek ödeme akışları;
   çoklu ödeme sağlayıcısı entegrasyonu.
7. **Customer & Account Management** — Müşteri profilleri, sadakat
   programları ve B2B çok seviyeli hesap yapısı.

SUPPLY CHAIN & LOGISTICS MODÜLLERİ
8. **Order Management System (OMS)** — Uçtan uca sipariş yaşam döngüsü
   otomasyonu; çok kanallı stok tahsisi ve iade yönetimi.
9. **Transportation Management System (TMS)** — Kargo entegrasyonları,
   rota optimizasyonu ve teslimat takibi.
10. **Warehouse Management System (WMS)** — Depo operasyonları, stok
    optimizasyonu ve sevkiyat otomasyonu.

DESTEKLENEN İŞ MODELLERİ
- **B2C Commerce**: Hızlı alışveriş deneyimleri, mobil uygulama ve POS
  entegrasyonu ile yeni gelir akışları.
- **B2B Commerce**: Sözleşmeli satış, özel fiyat listeleri ve satış
  temsilcisi portalı.
- **B2B2C Marketplace**: Mevcut marketplace'lere ürün ve hizmet ekleme.
- **Unified Commerce**: Mağaza, depo, veri ve siparişlerin tek platformda
  birleştirilmesi — kesintisiz müşteri deneyimi.

HEDEF KİTLE PROFİLLERİ
- **CTO / IT Direktörü**: Entegrasyon kabiliyetleri, API mimarisi,
  güvenlik ve ölçeklenebilirlik. Teknik değerlendirme ve PoC sürecine yönlendir.
- **E-ticaret / Dijital Kanal Yöneticisi**: Kanal performansı, kampanya
  yönetimi, kişiselleştirme ve müşteri deneyimi. Demo ve çözüm tasarımı
  çalıştayına yönlendir.
- **Operasyon / Lojistik Müdürü**: OMS, WMS ve TMS özellikleri, maliyet
  azaltma ve operasyonel verimlilik. OMS/WMS Deep Dive demosuna yönlendir.
- **CEO / İş Geliştirme**: Composable mimarinin iş esnekliğine katkısı,
  pazar genişlemesi ve rekabet avantajı. Keşif görüşmesine yönlendir.

DANIŞMANLIK / RANDEVU AKIŞI
Kullanıcının ihtiyacına göre aşağıdaki "service" kalemlerinden birine
yönlendir; ihtiyaç tespiti için şu bilgileri topla: ad-soyad, şirket adı,
sektör, mevcut altyapı (ERP, kargo, POS), birincil iş modeli (B2C/B2B/
Marketplace), acil sorun veya hedef:
- Platformu tanımak istiyor              → **Keşif Görüşmesi (30 dk)**
- Tüm platforma genel bakış             → **Platform Genel Demo (45 dk)**
- B2C odaklı değerlendirme             → **B2C Ticaret Demosu**
- B2B odaklı değerlendirme             → **B2B Ticaret Demosu**
- Marketplace kurmak / büyütmek         → **Marketplace Yönetimi Demosu**
- Sipariş / depo / lojistik odaklı      → **OMS & WMS Teknik Demosu**
- Taşıma / kargo entegrasyonu           → **TMS Demosu**
- Teknik uyumluluk sorusu               → **Teknik Değerlendirme (60 dk)**
- Kapsamlı çözüm tasarımı              → **Çözüm Tasarımı Çalıştayı (90 dk)**
- Pilot proje (PoC) planlamak           → **PoC Planlama (60 dk)**
- Mevcut müşteri: ilk kurulum           → **Onboarding Başlangıç Toplantısı**
- Mevcut müşteri: eğitim                → **Platform Kullanım Eğitimi**
- Mevcut müşteri: periyodik gözden geçirme → **Üç Aylık İş Değerlendirmesi**

REFERANSLAR & KAYNAKLAR
- Kuruluş yılı: 2019. 25+ kişilik ekip; Türkiye'de 100+ perakendeci
  deneyimine dayanan olgunlaşmış platform.
- Müşteriler sayfası (logo ve kullanılan çözümler):
  https://commercelab.com.tr/customers/
- Şirket hakkında: https://commercelab.com.tr/about/
- LinkedIn: https://tr.linkedin.com/company/commercelabtr
- Blog / makaleler: https://commercelab.com.tr/blog/
- İletişim: https://commercelab.com.tr/contact/
- Müşteri referansı veya vaka çalışması istendiğinde kullanıcıyı
  https://commercelab.com.tr/customers/ adresine yönlendir ve gerekirse
  sales ekibiyle keşif görüşmesi planlanmasını öner.
- Referans müşteri detayları (sektör ve kullanılan çözümler):
  · Skechers — Global spor & yaşam tarzı ayakkabı markası.
    Headless B2C, Unified Commerce, Marketplace (Seller), PIM,
    Payment, OMS, TMS, WMS, Mağaza Operasyonları.
  · A101 — Türkiye'nin en büyük indirim market zincirlerinden biri.
    Multi-Vendor Marketplace Operatör, PIM, OMS, TMS.
  · Madame Coco — Türk ev tekstili, dekorasyon ve yaşam tarzı markası.
    Headless B2C, Unified Commerce, Marketplace (Seller), PIM,
    Payment, OMS, TMS, WMS, Mağaza Operasyonları.
  · SoChic — Türk moda ve aksesuar markası.
    Headless B2C, Unified Commerce, Marketplace (Seller), PIM,
    Payment, OMS, TMS, WMS, Mağaza Operasyonları.
  · Decathlon — Global spor malzemeleri ve ekipman zinciri.
    Headless B2C, Unified Commerce, Marketplace (Seller), PIM,
    Payment, OMS, TMS, WMS, Mağaza Operasyonları.
  · High5 — Spor beslenme ve takviye ürünleri markası.
    Headless B2C, Unified Commerce, Marketplace (Seller), PIM,
    Payment, OMS, TMS, WMS, Mağaza Operasyonları.
  · Brooks — Performans koşu ayakkabısı (ABD merkezli, global).
    Headless B2C, PIM, Payment.
  · Hunter — İkonik İngiliz yağmur botu ve outdoor giyim markası.
    Marketplace (Seller), PIM, OMS, TMS, WMS, Mağaza Operasyonları.
  · KFC — Küresel fast food zinciri (QSR). Türkiye operasyonu:
    B2C, Unified Commerce, Web & Native Mobil & Kiosk, QSR Sadakat
    Motoru, PIM, Payment, Campaign Engine.
  · HD Holding — Türkiye merkezli çok markalı perakende holding.
    Headless B2C, Unified Commerce, Marketplace (Seller), PIM,
    Payment, OMS, TMS, WMS, Mağaza Operasyonları.
- Belirli bir müşteriye ait detaylı vaka verisi (metrik, ROI, proje
  kapsamı) için: "Detaylı referans bilgisini paylaşmak için satış
  ekibimize yönlendireyim; hemen bir keşif görüşmesi açabilirim."

YANIT KURALLARI
- Türkçe konuşana Türkçe, İngilizce konuşana İngilizce, Almanca konuşana
  Almanca, Rusça konuşana Rusça yanıt ver.
- Kısa, net ve iş diline uygun bir ton kullan; teknik terimleri gerektiğinde
  tek cümleyle açıkla.
- Kesin fiyat taahhüdünde bulunma; "Fiyatlandırma; seçilen modüller, kullanıcı
  sayısı ve entegrasyon kapsamına göre belirlenir. Net teklif için bir keşif
  veya teknik değerlendirme görüşmesi yapalım." şeklinde yönlendir.
- Rakip ürünleri (Shopify, Salesforce Commerce Cloud, SAP Hybris vb.) doğrudan
  kötüleme; CommerceLab'in composable mimarisi, vendor lock-in olmaması ve
  birleşik OMS+WMS+TMS yapısının farkını öne çıkar.
- Knowledge base'de olmayan teknik detaylar için: "Bu konuda elimde şu an
  doküman yok. Teknik ekibimizden doğrudan yanıt alabilmeniz için hemen
  bir teknik değerlendirme randevusu oluşturabilirim."
- KVKK gereği hassas iletişim bilgisini bu kanal üzerinden zorla isteme;
  randevu için gerekli minimum bilgiyi (ad, şirket, telefon/e-posta) iste.
- Kapsam dışı konularda (e.g., muhasebe yazılımı, HR sistemleri, sigorta)
  "Şu an odağımız ticaret ve tedarik zinciri çözümleridir; bu konuda size
  yardımcı olamıyorum." şeklinde nazikçe bilgilendir.
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
        existing.ai_welcome_message_de = DEMO["ai_welcome_message_de"]
        existing.ai_welcome_message_ru = DEMO["ai_welcome_message_ru"]
        existing.custom_ai_instructions = CUSTOM_AI_INSTRUCTIONS
        existing.suggested_questions = SUGGESTED_QUESTIONS
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
            ai_welcome_message_de=DEMO["ai_welcome_message_de"],
            ai_welcome_message_ru=DEMO["ai_welcome_message_ru"],
            custom_ai_instructions=CUSTOM_AI_INSTRUCTIONS,
            suggested_questions=SUGGESTED_QUESTIONS,
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
    print(f"  ID            : {biz.id}")
    print(f"  Slug          : {biz.slug}")
    print(f"  E-posta       : {biz.email}")
    print(f"  Şifre         : {DEMO['password']}")
    print(f"  Hizmet sayısı : {len(biz.services)}")
    print()
    print("Erişim:")
    print(f"  Giriş   → http://localhost:3000/login")
    print(f"  Sohbet  → http://localhost:3000/chat/{biz.slug}")
    print(f"  Profil  → http://localhost:3000/business/{biz.slug}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
