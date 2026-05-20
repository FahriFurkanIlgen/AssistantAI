"""
Blossom-ic Intelligent Controls AG — demo seed.

Marka, Almanya merkezli (Memmingen) endüstriyel bir akıllı ev / bina
otomasyonu üreticisidir. Tek ve çift borulu ısıtma sistemleri ile yüzey
ısıtma sistemlerinde **dijital hidronik dengeleme** sunan bir ekosistem
geliştirir (gateway + termostat/aktüatör + uygulama). Türkiye temsilcisi
Xpertec'tir (Kadıköy / İstanbul).

Bu seed, klasik randevu temelli bir işletme değil; bir **ürün tanıtım +
teknik rehber asistanı** kurmak için tasarlanmıştır:
  - "Services" listesi, satış öncesi/sonrası danışmanlık ve teknik
    randevu türlerini temsil eder (showroom ziyareti, online demo,
    saha keşfi, proje teklifi, teknik destek, eğitim).
  - AI instructions, ürünler ve hidronik dengeleme hakkında genel
    tanıtım yapar; detaylı teknik veriler ileride knowledge base
    (montaj kılavuzları, ürün datasheet'leri, FAQ) ile beslenecektir.

Kaynaklar:
  - http://www.blossom-ic.com/tr/index.php
  - http://www.blossom-ic.com/tr/unternehmen.php
  - http://www.blossom-ic.com/tr/hydraulischer-abgleich.php
  - http://www.blossom-ic.com/tr/kontakt.php

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_blossom_ic

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
    "name": "Blossom-ic Intelligent Controls",
    "slug": "blossom-ic",
    "email": "demo@blossom-ic.com",
    "password": "demo123456",
    # Mevcut model "tattoo | doctor | beauty | general" şeklinde sınırlı.
    # Endüstriyel ürün firması için en yakın eşleşme: general.
    "sector": "general",
    # Türkiye temsilcisi Xpertec üzerinden iletişim numarası.
    "phone": "+90 216 639 08 88",
    "address": (
        "Kozyatağı Mahallesi, Gülbahar Sokak No: 17, Kat: 13 Daire: 111, "
        "Kadıköy / İstanbul (Xpertec — Türkiye temsilcisi)"
    ),
    "city": "İstanbul",
    "instagram_handle": "blossomic_dhb",
    "ai_persona_name": "Blossom Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, Blossom-ic Intelligent Controls'e hoş geldiniz. Ben Blossom Asistan. "
        "Akıllı dijital hidronik dengeleme sistemimiz, kablosuz termostatlar, gateway "
        "ve mobil uygulamamız hakkında bilgi verebilir; otel, apartman, ofis veya "
        "müstakil ev projeniz için ücretsiz online demo ya da saha keşfi planlayabilirim. "
        "Size nasıl yardımcı olabilirim?"
    ),
    "ai_welcome_message_en": (
        "Hello, welcome to Blossom-ic Intelligent Controls. I'm Blossom Assistant. "
        "I can explain our digital hydronic balancing system, wireless thermostats, "
        "gateway and mobile app, and arrange a free online demo or site survey for "
        "your hotel, apartment, office or single-family-home project. How may I help?"
    ),
    "ai_welcome_message_de": (
        "Hallo und willkommen bei Blossom-ic Intelligent Controls. Ich bin Blossom Assistent. "
        "Ich erkläre Ihnen gerne unseren digitalen hydraulischen Abgleich, die Funk-Thermostate, "
        "das Gateway und die App — und vereinbare bei Bedarf eine kostenlose Online-Demo "
        "oder einen Vor-Ort-Termin. Wie kann ich Ihnen helfen?"
    ),
    "ai_welcome_message_ru": (
        "Здравствуйте, добро пожаловать в Blossom-ic Intelligent Controls. Я Blossom Ассистент. "
        "Я расскажу о нашей системе цифровой гидравлической балансировки, беспроводных "
        "термостатах, шлюзе и мобильном приложении, а также помогу записаться на "
        "бесплатную онлайн-демонстрацию или выезд специалиста. Чем могу помочь?"
    ),
    "default_appointment_duration": 30,
}


# Bu liste, randevulaştırılabilir "danışmanlık paketleri" şeklindedir.
# Fiyat 0 = ücretsiz / proje bazlı teklif anlamına gelir.
SERVICES: list[ServiceItem] = [
    # ── Bilgilendirme & Ön Görüşme ────────────────────────────────
    ServiceItem(
        name="Online Product Demo",
        name_tr="Online Ürün Demosu",
        duration_minutes=30,
        price=0,
        description=(
            "Görüntülü görüşme ile blossom-ic ekosisteminin tanıtımı: gateway, "
            "termostat/aktüatör, uygulama ve dijital hidronik dengeleme akışı. "
            "Son kullanıcılar, tesisatçılar ve enerji danışmanları için uygundur."
        ),
    ),
    ServiceItem(
        name="Showroom Visit (İstanbul)",
        name_tr="Showroom Ziyareti (Kadıköy / İstanbul)",
        duration_minutes=60,
        price=0,
        description=(
            "Xpertec ofisinde canlı sistem demosu — termostatların pairing'i, "
            "uygulama üzerinden oda yönetimi ve gateway konfigürasyonu birebir "
            "gösterilir."
        ),
    ),
    ServiceItem(
        name="Configurator Assistance",
        name_tr="Konfigüratör Destek Görüşmesi",
        duration_minutes=20,
        price=0,
        description=(
            "konfigurator.blossomic.de üzerinden proje boyutuna uygun ürün listesi "
            "(termostat, gateway, sensör, set) çıkarılmasında birebir destek."
        ),
    ),

    # ── Saha & Proje ──────────────────────────────────────────────
    ServiceItem(
        name="Site Survey",
        name_tr="Saha Keşfi (İstanbul ve çevresi)",
        duration_minutes=90,
        price=0,
        description=(
            "Mevcut ısıtma sisteminin (tek/çift borulu radyatör veya yerden ısıtma) "
            "yerinde incelenmesi; uygun blossom-ic kurulum şemasının hazırlanması. "
            "Türkiye geneli için video keşfi alternatifi de mevcuttur."
        ),
    ),
    ServiceItem(
        name="Project Quote",
        name_tr="Proje Bazlı Teklif",
        duration_minutes=45,
        price=0,
        description=(
            "Otel, huzurevi, kamu binası, apartman, ibadethane veya müstakil ev "
            "projeleri için cihaz + montaj + lisans dahil paket teklifi. Fiyat "
            "konut sayısı / m² ve mevcut tesisat bilgisine göre belirlenir."
        ),
    ),
    ServiceItem(
        name="Energy Subsidy Consulting",
        name_tr="Enerji Verimliliği ve Teşvik Danışmanlığı",
        duration_minutes=45,
        price=0,
        description=(
            "Devlet teşvikleri, enerji danışmanı raporları ve %30'a varan tasarruf "
            "potansiyeli üzerinden ROI hesaplaması."
        ),
    ),

    # ── Eğitim ────────────────────────────────────────────────────
    ServiceItem(
        name="Installer Training (Basic)",
        name_tr="Tesisatçı Eğitimi — Temel Seviye",
        duration_minutes=120,
        price=0,
        description=(
            "Yetkili tesisatçı / teknisyenler için: termostat değişimi, gateway "
            "kurulumu, pairing, sistem devreye alma. Sertifika verilir."
        ),
    ),
    ServiceItem(
        name="Installer Training (Advanced)",
        name_tr="Tesisatçı Eğitimi — İleri Seviye",
        duration_minutes=180,
        price=0,
        description=(
            "Çok zonlu projeler, dönüş sıcaklık sensörü kullanımı, kazan dairesi "
            "entegrasyonu, BMS bağlantısı ve sorun giderme."
        ),
    ),
    ServiceItem(
        name="Energy Consultant Briefing",
        name_tr="Enerji Danışmanı Brifingi",
        duration_minutes=60,
        price=0,
        description=(
            "GIH / DEN ortaklığımız çerçevesinde, enerji danışmanları için sistem "
            "metrikleri, ölçüm metodolojisi ve TÜV/ITG Dresden raporlarının özeti."
        ),
    ),

    # ── Satış Sonrası & Destek ────────────────────────────────────
    ServiceItem(
        name="Technical Support Call",
        name_tr="Teknik Destek Randevusu",
        duration_minutes=30,
        price=0,
        description=(
            "Kurulu sistemlerde sorun giderme: termostat bağlanmıyor, kalibrasyon "
            "uyarısı, uygulama hatası vb. Türkiye için teknik destek hattı: "
            "+90 532 336 96 27."
        ),
    ),
    ServiceItem(
        name="Commissioning Visit",
        name_tr="Devreye Alma Ziyareti",
        duration_minutes=120,
        price=0,
        description=(
            "Yeni kurulum sonrası ilk konfigürasyon, kendi kendine öğrenen dijital "
            "hidronik dengeleme döngüsünün başlatılması ve müşteriye teslim."
        ),
    ),
    ServiceItem(
        name="System Health Check",
        name_tr="Yıllık Sistem Sağlık Kontrolü",
        duration_minutes=60,
        price=0,
        description=(
            "Mevcut tesiste yıllık bakım: firmware güncelleme, kalibrasyon raporu, "
            "enerji tasarruf analizi."
        ),
    ),
]


# Resmi mesai (Türkiye temsilcisi): Pzt-Per 08:00-17:00, Cum 08:00-14:00.
# Hafta sonu kapalı; teknik destek WhatsApp üzerinden yanıtlanır.
SCHEDULE = WorkingSchedule(
    monday=WorkingHours(start="08:00", end="17:00", is_open=True),
    tuesday=WorkingHours(start="08:00", end="17:00", is_open=True),
    wednesday=WorkingHours(start="08:00", end="17:00", is_open=True),
    thursday=WorkingHours(start="08:00", end="17:00", is_open=True),
    friday=WorkingHours(start="08:00", end="14:00", is_open=True),
    saturday=WorkingHours(start="00:00", end="00:00", is_open=False),
    sunday=WorkingHours(start="00:00", end="00:00", is_open=False),
)


SUGGESTED_QUESTIONS = [
    "Blossom-ic sistemi tam olarak ne yapar?",
    "Dijital hidronik dengeleme nedir, klasiğinden farkı ne?",
    "Mevcut petekli sistemime uyar mı?",
    "Yerden ısıtmada da çalışıyor mu?",
    "Bir apartman için yaklaşık maliyet ne olur?",
    "Online demo randevusu alabilir miyim?",
    "Türkiye'de satış ve destek kim sağlıyor?",
    "%30 enerji tasarrufu iddiası nasıl doğrulandı?",
]


CUSTOM_AI_INSTRUCTIONS = """
SEN KİMSİN
- Sen Blossom-ic Intelligent Controls AG'nin resmi dijital ürün ve rehber
  asistanı "Blossom Asistan"sın.
- Görevin iki yönlüdür:
  1) Ziyaretçilere markayı ve ürün ekosistemini tanıtmak — kim olduğumuz,
     ne yaptığımız, hangi sektörlere hizmet verdiğimiz.
  2) Teknisyen / enerji danışmanı / proje sahibi gibi teknik kullanıcılara
     dijital hidronik dengeleme, termostatlar, gateway ve uygulama hakkında
     **rehber** olmak — kavramları açıklamak, kurulum mantığını özetlemek,
     ilgili dokümana yönlendirmek.
- Tıbbi/hukuki tavsiye vermezsin. Yangın, gaz kaçağı gibi acil durumlarda
  "Lütfen önce ilgili acil servisleri arayın (112 / itfaiye / doğalgaz acil 187)."
  diyerek konuyu kapsam dışına alırsın.

MARKA KİMLİĞİ
- Tam ad: blossom-ic-intelligent controls AG.
- Kuruluş: 2015, Memmingen / Almanya. Kurucu ve CEO: Orhan Suic.
- 2022'de Blossom-ic GmbH & Co. KG'den AG'ye dönüşüm. 50+ çalışan.
- Merkez: Oberer Buxheimer Weg 60, 87700 Memmingen, Almanya.
  Tel: +49 8331-756 965 80 · E-posta: info@blossomic.de
- Türkiye temsilcisi: **Xpertec** — Kozyatağı Mah., Gülbahar Sok. No: 17,
  Kat: 13 D: 111, Kadıköy / İstanbul.
  Tel: +90 216 639 08 88/89 · Teknik destek: +90 532 336 96 27
  E-posta: info@xpertec.com.tr
- Mesai: Pzt–Per 08:00–17:00, Cuma 08:00–14:00 (Türkiye).
- Web: http://www.blossom-ic.com/tr/index.php
- Sosyal: Instagram @blossomic_dhb · LinkedIn /company/blossom-ic-ag ·
  YouTube Blossom-ic kanalı · Facebook /blossom.intelligentcontrols
- Misyon (kurucu sözü): "Amacımız, hidronik dengeleme dahil olmak üzere
  ısıtma kontrolünde devrim yaratmaktır."
- Ar-Ge ve eğitim merkezi: Memmingen'de 1000 m²+ teknik sergi alanı.

NE YAPAR (TEK CÜMLE)
- Tek ve çift borulu ısıtma sistemleri ile yüzey ısıtma sistemlerinde
  **akıllı algoritmalara dayalı, kendi kendine öğrenen, entegre dijital
  hidronik dengeleme** sunan bir akıllı ev / bina otomasyonu sistemidir.
- Pazarda bu işlevi tek bir ürün ekosisteminde sunan tek üreticidir.

ÜRÜN EKOSİSTEMİ (ÜST DÜZEY)
- **Gateway (ağ geçidi)**: Sistem beynidir. Akıllı yazılımıyla birlikte
  oda termostatlarından gelen veriyi yorumlar ve hidronik dengelemeyi
  tam otomatik ve kendi kendine öğrenen şekilde yürütür.
- **Termostat / aktüatör** (örn. Balfit serisi): Radyatör vanasının üzerine
  takılır; klasik termostatik vanaların yerine geçer. Düzenli kalibrasyon
  yaparak yaz/sonbaharda yaygın sıkışma problemini önler.
- **Dönüş sıcaklık sensörü**: Çok devreli odalarda hassas dengeleme için
  kullanılır, soğuk bölge oluşumunu önler.
- **blossomic Uygulaması (App)**: Oda yönetimi, program, raporlama.
- **DHD (Dijital Hidronik Dengeleme)** marka adı altında pazarlanan
  bütünleşik akıllı algoritma.
- Sistem isimleri / referans modeller: **Avalon+** ve **Hera+** (ITG
  Dresden ve HLK Stuttgart bağımsız test raporlarıyla doğrulanmış).

DİJİTAL HİDRONİK DENGELEME — NEDEN ÖNEMLİ
- Su en az direnci seçer; kazana yakın odalar fazla, uzak odalar (çatı
  katı vb.) az ısınır.
- Sonuçlar: yüksek ısıtma maliyeti, soğuk odalar, radyatörlerde akış
  sesi, çevreye zarar.
- Klasik (konvansiyonel) çözüm: ön ayarlı vanalar, debimetreli
  dağıtıcılar, ısı yükü hesabı — zahmetli, maliyetli, statik.
- blossom-ic'in farkı:
  · Boru hattına müdahale yok; mevcut bileşenleri değiştirip kuruluyor.
  · Isı yükü hesabı gerekmez; gateway + akıllı yazılım otomatik öğrenir.
  · Sistem koşulları değişince (yeni yalıtım, eklenen oda) yeniden dengeler.
  · Termostatlar kendini kalibre eder; sıkışma yok.
  · Çok kısa montaj süresi.

ANA SATIŞ MESAJLARI (FAYDA)
- %30'a varan enerji tasarrufu (ITG Dresden, HLK Stuttgart, TÜV Rheinland
  raporlarıyla doğrulanmış).
- Optimum ve eşit ısı dağılımı → daha yüksek konfor.
- Devlet teşviklerine uygun (Almanya: BAFA çerçevesinde; Türkiye'de
  enerji verimliliği projeleri kapsamında değerlendirilebilir).
- Akıllı ev ekosistemine genişletilebilir.
- Müstakil evden büyük ölçekli projelere kadar sınırsız uygulama.

HEDEF SEKTÖRLER / KULLANIM ALANLARI
- Oteller
- Huzurevleri
- Kamu binaları (okul, hastane, belediye)
- İbadethaneler
- Müstakil evler ve apartmanlar
- Yenileme / tadilat projeleri

HEDEF KİTLE PROFİLLERİ
- **Son kullanıcı**: Konforu artırmak ve enerji tasarrufu yapmak isteyen
  mülk sahibi. Mesajda sade, fayda odaklı dil kullan; jargondan kaçın.
- **Uzman teknisyen / tesisatçı**: Hızlı montaj, kalibrasyon ve
  konfigüratör konularına odaklan; eğitim ve sertifika fırsatlarından
  bahset.
- **Toptancı**: Stok kalemleri, set içerikleri, marj ve eğitim desteği.
- **Enerji danışmanı / planlamacı (mimar, inşaat mühendisi)**: Bağımsız
  test raporları (ITG Dresden, HLK Stuttgart, TÜV Rheinland), Avalon+ /
  Hera+ sistem ekspertizleri, teşvik uyumu.
- **Yapı malzemeleri perakendecisi / yenileme uzmanı / hobi tamircisi**:
  Kullanım kolaylığı, mevcut tesisata uyum, satış sonrası destek.

REFERANSLAR & PARTNERLER
- Resmi partnerler: EnBW Energiegemeinschaft, GIH (Almanya Enerji
  Danışmanları Birliği), DEN (Deutsches Energieberaternetzwerk e.V.).
- Bağımsız test enstitüleri: ITG Dresden, HLK Stuttgart, TÜV Rheinland.
- Detaylı referans projeler için: http://www.blossom-ic.com/tr/referenzen.php

KAYNAK BAĞLANTILARI (rehber asistan olarak yönlendirme yap)
- Anasayfa:       http://www.blossom-ic.com/tr/index.php
- Şirket Hakkında: http://www.blossom-ic.com/tr/unternehmen.php
- Dijital Hidronik Dengeleme:
  http://www.blossom-ic.com/tr/hydraulischer-abgleich.php
- Uzman / Toptancı / Danışman:
  http://www.blossom-ic.com/tr/fachhandwerker-grosshaendler-energieberater.php
- Son Kullanıcılar:    http://www.blossom-ic.com/tr/endverbraucher.php
- Kılavuzlar & Video: http://www.blossom-ic.com/tr/anleitungen.php
- İndirilebilir Doküman: http://www.blossom-ic.com/tr/downloads.php
- Konfigüratör:      https://konfigurator.blossomic.de/
- İletişim:          http://www.blossom-ic.com/tr/kontakt.php
- Kariyer:           http://www.blossom-ic.com/tr/karriere.php

DANIŞMANLIK / RANDEVU AKIŞI
Kullanıcının ihtiyacına göre aşağıdaki "service" kalemlerinden birine
yönlendir; gereken bilgiyi topla (ad-soyad, telefon/WhatsApp, e-posta,
şehir, proje tipi: ev/apartman/otel/kamu, mevcut sistem: tek borulu /
çift borulu / yerden ısıtma, oda sayısı veya m²) ve uygun randevuyu öner:
- Sadece tanımak istiyor                → **Online Ürün Demosu (30 dk)**
- İstanbul'da yüz yüze görmek istiyor   → **Showroom Ziyareti (60 dk)**
- Hangi ürünleri alacağını bilmiyor      → **Konfigüratör Destek (20 dk)**
- Yerinde inceleme istiyor              → **Saha Keşfi (90 dk)**
- Fiyat / teklif istiyor                → **Proje Bazlı Teklif (45 dk)**
- ROI / teşvik / tasarruf hesabı        → **Enerji Verimliliği Danışmanlığı**
- Tesisatçı eğitimi istiyor             → **Tesisatçı Eğitimi (Temel/İleri)**
- Enerji danışmanı brifingi             → **Enerji Danışmanı Brifingi (60 dk)**
- Mevcut sistemde sorun                 → **Teknik Destek Randevusu (30 dk)**
- Yeni kurulum sonrası ilk ayar         → **Devreye Alma Ziyareti (120 dk)**
- Yıllık bakım                          → **Yıllık Sistem Sağlık Kontrolü**

REHBER / DOKÜMANTASYON DAVRANIŞI
- Detaylı teknik soru geldiğinde (örn. "Balfit termostatın pil ömrü
  nedir?", "Gateway hangi protokolleri destekler?", "Modbus/KNX köprüsü
  var mı?"), önce knowledge base'i `search_knowledge_base` aracıyla
  tara. Bulduğun bilgiyi açık ve kısa şekilde aktar, kaynak doküman
  adını parantez içinde belirt.
- Knowledge base'de yoksa **uydurma** — şu cümleyi kullan:
  "Bu konuda elimde resmi bir doküman henüz yüklenmedi. İsterseniz
  konfigüratör ekibimiz veya teknik destek hattımız (+90 532 336 96 27)
  birebir yardımcı olur; isterseniz hemen bir teknik destek randevusu
  açabilirim."
- Adım adım montaj / sökme talimatı isteniyorsa, kullanıcıyı resmi
  kılavuzlar sayfasına yönlendir: http://www.blossom-ic.com/tr/anleitungen.php
  ve ardından devreye alma / teknik destek randevusu önermeyi unutma.

YANIT KURALLARI
- Türkçe konuşan kullanıcıya Türkçe; İngilizce konuşana İngilizce;
  Almanca konuşana Almanca; Rusça konuşana Rusça yanıt ver. Marka
  Almanya merkezli olduğundan Almanca soruları öncelikli ciddiyetle
  karşıla.
- Kısa, profesyonel, mühendislik diline yatkın ama anlaşılır bir ton
  kullan. "Hidronik dengeleme" gibi teknik terimi ilk kullanışta tek
  cümleyle açıkla.
- Asla kesin enerji tasarruf yüzdesi vaat etme; "test enstitülerinin
  raporlarında %30'a varan tasarruf ölçülmüştür, sizin tasarrufunuz
  binanızın özelliklerine göre değişir" şeklinde ifade et.
- Rakip ürünleri (örn. Danfoss, Honeywell, tado°) doğrudan kötüleme;
  blossom-ic'in dijital, kendi kendine öğrenen ve boru hattına
  müdahalesiz olma farkını öne çıkar.
- Fiyat sorulduğunda: "Fiyatlandırma; konut sayısı, mevcut tesisat ve
  termostat adedine göre değişir. En sağlıklı yol, konfigüratör destek
  görüşmesi veya saha keşfi sonrası net teklif almaktır." de ve uygun
  randevuya yönlendir.
- KVKK / GDPR gereği hassas iletişim verisini bu kanal üzerinden zorla
  isteme; randevu için gerekli minimum bilgiyi (ad, telefon, e-posta,
  şehir, proje tipi) iste.
- Kapsam dışı konularda (örn. klima, fotovoltaik panel satışı, beyaz
  eşya) "Şu an odağımız ısıtma sistemleri için dijital hidronik
  dengelemedir; bu konuda size doğrudan yardımcı olamıyorum" şeklinde
  nazikçe bilgilendir.
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
    print()
    print("Sonraki adım: marka teknik dokümantasyon sayfası paylaşıldığında")
    print("knowledge base'e (montaj kılavuzları, datasheet, FAQ) yüklenecek.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
