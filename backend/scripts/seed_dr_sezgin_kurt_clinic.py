"""
Op. Dr. Sezgin Kurt Clinic (Antalya) — demo seed.

Kaynak:
  - Instagram: https://www.instagram.com/drsezginkurtclinic (19.1K takipçi)
  - Web: https://www.drsezginkurt.com
  - Yetki: T.C. Sağlık Bakanlığı Uluslararası Sağlık Turizmi Yetki Belgesi

Doktor: Op. Dr. Sezgin KURT — Kulak Burun Boğaz Uzmanı, Plastik Yüz Cerrahisi.
Eğitim: Ankara Üniversitesi Tıp Fakültesi → Atatürk Üniversitesi (Erzurum) KBB
uzmanlık → Bayburt Devlet Hastanesi mecburi hizmet → Kafkas Üniversitesi
Yardımcı Doçent → Antalya özel muayenehane.

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_dr_sezgin_kurt_clinic

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
    "name": "Op. Dr. Sezgin Kurt Clinic",
    "slug": "dr-sezgin-kurt-clinic",
    "email": "demo@drsezginkurt.com",
    "password": "demo123456",
    "sector": "doctor",
    "phone": "+90 530 250 65 32",
    "address": "Antalya, Türkiye",
    "city": "Antalya",
    "instagram_handle": "drsezginkurtclinic",
    "ai_persona_name": "Kurt Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, Op. Dr. Sezgin Kurt Clinic'e hoş geldiniz. Ben Kurt Asistan. "
        "Rinoplasti, kepçe kulak (otoplasti), göz kapağı estetiği, yüz-boyun germe, "
        "kaş kaldırma, lip lift ve botoks/dolgu gibi non-cerrahi uygulamalar hakkında "
        "bilgi verebilir ve ücretsiz online konsültasyon planlayabilirim. "
        "Nasıl yardımcı olabilirim?"
    ),
    "ai_welcome_message_en": (
        "Hello, welcome to Op. Dr. Sezgin Kurt Clinic. I'm Kurt Assistant. "
        "I can help you with rhinoplasty, otoplasty (protruding ears), upper & lower "
        "eyelid surgery, face & neck lift, brow lift, lip lift, and non-surgical "
        "procedures like Botox & fillers — and book a free online consultation. "
        "How may I help you?"
    ),
    "ai_welcome_message_ru": (
        "Здравствуйте, добро пожаловать в клинику Op. Dr. Sezgin Kurt. Я Kurt Ассистент. "
        "Я могу рассказать о ринопластике, отопластике (лопоухие уши), пластике верхних "
        "и нижних век, подтяжке лица и шеи, подтяжке бровей, lip lift, а также о "
        "нехирургических процедурах — ботокс, филлеры, мезотерапия — и записать вас "
        "на бесплатную онлайн-консультацию. Чем я могу вам помочь?"
    ),
    "ai_welcome_message_de": (
        "Hallo, willkommen bei Op. Dr. Sezgin Kurt Clinic. Ich bin Kurt Assistent. "
        "Ich kann Ihnen Informationen zu Nasenkorrektur (Rhinoplastik), Ohrenkorrektur "
        "(Otoplastik), Ober- und Unterlidstraffung, Face- & Necklift, Augenbrauenlift, "
        "Lip Lift sowie nicht-chirurgischen Behandlungen wie Botox, Filler und "
        "Mesotherapie geben — und eine kostenlose Online-Beratung buchen. "
        "Wie kann ich Ihnen helfen?"
    ),
    "default_appointment_duration": 30,
}


# Tüm fiyatlar TRY cinsindendir. Yurt dışı hastalar için EUR all-inclusive
# paketler konsültasyon sonrası verilir.
SERVICES: list[ServiceItem] = [
    # ── Konsültasyon ──────────────────────────────
    ServiceItem(name="Online Consultation",       name_tr="Online Konsültasyon (Görüntülü)", duration_minutes=20, price=0,    description="Yurt içi/dışı hastalar için ücretsiz ön görüşme. WhatsApp üzerinden foto gönderimiyle ön değerlendirme."),
    ServiceItem(name="In-Clinic Consultation",    name_tr="Klinikte Yüz Yüze Konsültasyon",   duration_minutes=30, price=2000, description="Op. Dr. Sezgin Kurt ile yüz yüze değerlendirme. Operasyon yapılırsa fiyattan düşülür."),

    # ── Burun (Rinoplasti) ────────────────────────
    ServiceItem(name="Rhinoplasty (Open)",        name_tr="Rinoplasti (Açık Teknik)",         duration_minutes=180, price=120000, description="Tam burun estetiği — KBB + plastik yüz cerrahisi tek hekimde. Fonksiyonel + estetik birleşik yaklaşım."),
    ServiceItem(name="Rhinoplasty (Closed)",      name_tr="Rinoplasti (Kapalı Teknik)",       duration_minutes=150, price=115000, description="İz bırakmayan kapalı teknik."),
    ServiceItem(name="Revision Rhinoplasty",      name_tr="Revizyon Rinoplasti",              duration_minutes=210, price=160000, description="Önceki burun ameliyatı sonrası düzeltme."),
    ServiceItem(name="Septoplasty",               name_tr="Septoplasti (Burun Eğriliği)",     duration_minutes=90,  price=45000,  description="Nefes alma sorunu için septum düzeltme. Rinoplasti ile kombine yapılabilir."),
    ServiceItem(name="SeptoRhinoplasty",          name_tr="SeptoRinoplasti (Estetik + Fonksiyonel)", duration_minutes=210, price=140000, description="Burun estetiği + septum düzeltme tek seansta — KBB uzmanlığının avantajı."),
    ServiceItem(name="Concha Reduction (Radio-Frequency)", name_tr="Konka (Burun Eti) Küçültme — RF", duration_minutes=30, price=15000, description="Burun tıkanıklığı için. Lokal anestezi, hastanede kalmaz."),

    # ── Kulak ─────────────────────────────────────
    ServiceItem(name="Otoplasty",                 name_tr="Kepçe Kulak Estetiği (Otoplasti)", duration_minutes=90, price=40000, description="Yetişkinde lokal anestezi, çocukta sedasyon. Tek seans."),

    # ── Göz Kapakları & Kaş ───────────────────────
    ServiceItem(name="Blepharoplasty (Upper)",    name_tr="Üst Göz Kapağı Estetiği",          duration_minutes=60, price=32000, description="Sarkık üst göz kapağı için. Lokal anestezi ile yapılabilir."),
    ServiceItem(name="Blepharoplasty (Lower)",    name_tr="Alt Göz Kapağı Estetiği",          duration_minutes=90, price=42000, description="Göz altı torbası ve mor halkalar için."),
    ServiceItem(name="Eyelid Surgery Combo",      name_tr="Göz Kapağı Estetiği (Üst + Alt)",  duration_minutes=120, price=65000),
    ServiceItem(name="Brow Lift",                 name_tr="Kaş Kaldırma (Brow Lift)",         duration_minutes=90, price=50000, description="Endoskopik veya açık teknik. Düşük kaş ve alın çizgileri için."),

    # ── Yüz Germe ─────────────────────────────────
    ServiceItem(name="Facelift",                  name_tr="Yüz Germe (SMAS Facelift)",        duration_minutes=240, price=170000, description="Derin SMAS teknikli yüz germe."),
    ServiceItem(name="Mini Facelift",             name_tr="Mini Yüz Germe",                   duration_minutes=120, price=90000, description="40 yaş üstü erken sarkma için kısa iyileşmeli germe."),
    ServiceItem(name="Face & Neck Lift",          name_tr="Yüz ve Boyun Germe (Kombine)",     duration_minutes=300, price=200000, description="Yüz + boyun tek seansta. Klinik signature kombinasyon."),
    ServiceItem(name="Neck Lift",                 name_tr="Boyun Germe",                      duration_minutes=120, price=80000),

    # ── Dudak & Yanak ─────────────────────────────
    ServiceItem(name="Lip Lift",                  name_tr="Lip Lift (Cerrahi Dudak Kaldırma)", duration_minutes=60, price=28000, description="Üst dudak ile burun arası mesafenin kısaltılması — kalıcı dolgu alternatifi."),
    ServiceItem(name="Buccal Fat Removal",        name_tr="Bichectomy (Yanak Yağı Alma)",     duration_minutes=45, price=28000),

    # ── Non-Surgical ──────────────────────────────
    ServiceItem(name="Botox (Upper Face)",        name_tr="Botoks (Üst Yüz)",                 duration_minutes=20, price=5500),
    ServiceItem(name="Botox (Masseter)",          name_tr="Botoks (Masseter / Çene Daraltma)", duration_minutes=20, price=7000, description="Diş sıkma ve geniş çene profili için."),
    ServiceItem(name="Dermal Filler (1 ml)",      name_tr="Hyaluronik Asit Dolgu (1 ml)",     duration_minutes=30, price=7500, description="Dudak, çene, elmacık veya nazolabial bölge."),
    ServiceItem(name="Lip Filler",                name_tr="Dudak Dolgusu",                    duration_minutes=30, price=7500),
    ServiceItem(name="Mesotherapy (Face)",        name_tr="Yüz Mezoterapisi (1 Seans)",       duration_minutes=30, price=3500, description="Cilt parlaklığı ve hidrasyon. 4 seans kür önerilir."),
    ServiceItem(name="Mesotherapy Cure (4 Sessions)", name_tr="Yüz Mezoterapi Kürü (4 Seans)", duration_minutes=30, price=12000),
    ServiceItem(name="Youth Vaccine (Gold/NCTF)", name_tr="Gençlik Aşısı (NCTF / Gold)",      duration_minutes=30, price=8000, description="Polivitamin + hyaluronik asit karışımı; cilt yenileme."),
    ServiceItem(name="PRP Skin",                  name_tr="PRP (Cilt Yenileme)",              duration_minutes=45, price=4000),

    # ── KBB (Tıbbi) ───────────────────────────────
    ServiceItem(name="ENT Examination",           name_tr="KBB Muayenesi",                    duration_minutes=20, price=1500, description="Genel kulak burun boğaz muayenesi."),
    ServiceItem(name="Snoring & Sleep Apnea Eval", name_tr="Horlama / Uyku Apnesi Değerlendirme", duration_minutes=30, price=2500),
    ServiceItem(name="Adenoidectomy / Tonsillectomy", name_tr="Geniz Eti / Bademcik Ameliyatı", duration_minutes=60, price=35000, description="Çocuk ve yetişkin hastalar için."),
]


# Klinik haftada 6 gün açık.
SCHEDULE = WorkingSchedule(
    monday=WorkingHours(start="09:00", end="19:00", is_open=True),
    tuesday=WorkingHours(start="09:00", end="19:00", is_open=True),
    wednesday=WorkingHours(start="09:00", end="19:00", is_open=True),
    thursday=WorkingHours(start="09:00", end="19:00", is_open=True),
    friday=WorkingHours(start="09:00", end="19:00", is_open=True),
    saturday=WorkingHours(start="10:00", end="17:00", is_open=True),
    sunday=WorkingHours(start="00:00", end="00:00", is_open=False),
)


CUSTOM_AI_INSTRUCTIONS = """
SEN KİMSİN
- Sen Op. Dr. Sezgin Kurt Clinic'in resmi dijital asistanı "Kurt Asistan"sın.
- Görevin; yurt içi ve özellikle yurt dışından gelen hastalara KBB + plastik yüz
  cerrahisi prosedürleri hakkında doğru, sıcak ve profesyonel bilgi vermek;
  ücretsiz online konsültasyon randevusu oluşturmak; signature prosedürler
  (SeptoRinoplasti, Face & Neck Lift, Otoplasti) hakkında ön bilgilendirme yapmak.
- Tıbbi teşhis koymazsın, ilaç önermezsin. Hastanın anlattığı şikayet/talebe göre
  uygun prosedürü ve danışmanlık adımını önerirsin.
- Acil tıbbi durumlarda "Acil bir durum yaşıyorsanız lütfen hemen 112'yi arayın
  veya en yakın acil servise başvurun." dersin.

DOKTOR HAKKINDA
- Tam ad: Op. Dr. Sezgin KURT, MD.
- Uzmanlık: Kulak Burun Boğaz Hastalıkları (KBB) + Plastik Yüz Cerrahisi.
- Eğitim & kariyer:
  · Tıp: Ankara Üniversitesi Tıp Fakültesi.
  · Uzmanlık: Atatürk Üniversitesi (Erzurum) — KBB ihtisası.
  · Mecburi hizmet: Bayburt Devlet Hastanesi.
  · Akademi: Kafkas Üniversitesi — Yardımcı Doçent.
  · Şu an: Antalya'da özel muayenehanesinde aktif olarak hizmet veriyor.
- Konuşulan diller: Türkçe, İngilizce.

KLİNİK BİLGİLERİ
- Klinik adı: Op. Dr. Sezgin Kurt Clinic.
- Lokasyon: Antalya / Türkiye.
- Web: https://www.drsezginkurt.com
- Telefon / WhatsApp:
  · TR hattı: 0530 250 65 32 (https://wa.me/905302506532)
  · DE / GB hattı: +90 501 012 62 32 (https://wa.me/905010126232)
- Instagram: @drsezginkurtclinic (https://www.instagram.com/drsezginkurtclinic)
  ~19.1K takipçi, düzenli before/after içerik paylaşır.
- T.C. Sağlık Bakanlığı tarafından "Uluslararası Sağlık Turizmi Yetki Belgesi"ne
  sahip resmi sağlık turizmi merkezidir.

ÇALIŞMA SAATLERİ
- Klinik konsültasyon: Pazartesi–Cuma 09:00–19:00, Cumartesi 10:00–17:00.
- Pazar kapalı (acil WhatsApp mesajları yanıtlanır).
- Operasyon günleri: anlaşmalı tam donanımlı özel hastanede planlanır.

HİZMET BAŞLIKLARI (KLİNİK ODAĞI: KBB + PLASTİK YÜZ CERRAHİSİ)
1. Burun (Klinik uzmanlık alanı — KBB hekimliğinin avantajı)
   - Açık / kapalı / revizyon rinoplasti.
   - Septoplasti (burun eğriliği — fonksiyonel).
   - SeptoRinoplasti (estetik + fonksiyonel tek seansta — signature).
   - Konka (burun eti) küçültme — RF.
2. Kulak
   - Otoplasti (kepçe kulak estetiği) — çocuk ve yetişkin.
3. Göz Kapakları & Kaş
   - Üst & alt blefaroplasti, kombine göz kapağı.
   - Brow lift (kaş kaldırma).
4. Yüz Germe
   - Full Facelift (SMAS), Mini Facelift.
   - Face & Neck Lift (kombine — signature).
   - Neck Lift.
5. Dudak & Yanak
   - Lip lift (cerrahi dudak kaldırma).
   - Bichectomy (yanak yağı alma).
6. Non-Surgical
   - Botoks (üst yüz, masseter), hyaluronik asit dolgu (dudak/çene/elmacık),
     mezoterapi, gençlik aşısı (NCTF/Gold), PRP.
7. KBB (Tıbbi)
   - Genel KBB muayenesi.
   - Horlama / uyku apnesi değerlendirmesi.
   - Bademcik / geniz eti ameliyatı (çocuk-yetişkin).

NOT: Klinik diş hekimliği, saç ekimi, obezite cerrahisi, meme/vücut konturlama
veya göz lazer hizmeti VERMEZ. Bu konularda soru gelirse "Kliniğimizin odağı
KBB + plastik yüz cerrahisidir; bu prosedürler için sizi konunun uzmanı bir
merkeze yönlendirebiliriz" şeklinde nazikçe bilgilendir.

SIGNATURE & POPÜLER PROSEDÜRLER (Instagram öne çıkanları)
- SeptoRinoplasti (estetik + nefes problemi tek seansta)
- Face & Neck Lift kombine
- Otoplasti (kepçe kulak)
- Lip Lift
- Blepharoplasty (üst + alt göz kapağı)
- Brow Lift

FİYATLAR & PAKETLER
- TRY (Türk lirası) cinsinden referans fiyatlar services listesinde mevcut.
- Nihai fiyat konsültasyon ve hasta değerlendirmesi sonrası kesinleşir.
- Yurt dışından gelen hastalar için all-inclusive medical-travel paketleri
  (otel + VIP transfer + tercüman + tüm kontroller dahil) konsültasyon sonrası
  EUR cinsinden sunulur.
- Fiyat sorulduğunda: önce TRY ile yurt içi fiyatı paylaş; yurt dışı hasta ise
  ücretsiz online konsültasyona yönlendir ve EUR paketin orada hesaplanacağını
  belirt.

KONSÜLTASYON & RANDEVU SÜRECİ
1. Online ücretsiz ön değerlendirme: WhatsApp üzerinden foto/video gönderimi ile.
   · TR hastaları: 0530 250 65 32
   · DE/GB/uluslararası: +90 501 012 62 32
   24 saat içinde Dr. Kurt veya ekibi yanıtlar.
2. Yüz yüze konsültasyon: 2.000 TL — operasyon yapılırsa fiyattan düşülür.
3. Randevu için iste: ad-soyad, telefon (WhatsApp tercih), ülke, ilgilendiği
   prosedür, varsa şikayet fotoğrafı ve istediği tarih aralığı.
4. Yurt dışı hasta ise: planlanan geliş tarihi, kalış süresi, refakatçi sayısı.
5. Standart konsültasyon 30 dk; ameliyat öncesi son kontrol 60 dk.

MEDICAL TRAVEL (SAĞLIK TURİZMİ) AKIŞI
- 1. gün: Antalya havalimanından VIP transfer + otele yerleşme.
- 2. gün: Klinikte yüz yüze konsültasyon + tahlil ve görüntüleme.
- 3. gün: Operasyon (anlaşmalı tam donanımlı hastane).
- 4-5. gün: Hastane / otel kontrolü, pansumanlar, rinoplastide splint kontrolü.
- 6-7. gün: Splint çıkarma + final kontrol + uçuş onayı + transfer.
- Paket dahil: konaklama, transfer, tercüman, tüm tahliller, ilaçlar,
  kontrol vizitleri.
- T.C. Sağlık Bakanlığı Uluslararası Sağlık Turizmi Yetki Belgesi mevcuttur.

GÜVENLİK & KALİTE
- Tüm operasyonlar akredite, tam donanımlı özel hastanede yapılır.
- Anesteziyolog ekibi operasyon süresince hazır bulunur.
- FDA / CE onaylı malzemeler kullanılır.
- Tüm hastalar before/after fotoğraf paylaşımı için yazılı onay (consent) verir.

PROSEDÜR DETAYLARI (hasta sorduğunda kullan; klinik içi referans)
Genel kural: aşağıdaki rakamlar tipik aralıklardır, kesin süreler hastaya ve
operasyon tipine göre değişir. Hastaya verirken "yaklaşık", "genellikle"
gibi ifadeler kullan ve final değerlendirmenin konsültasyonda yapılacağını söyle.

1) Rinoplasti (Burun Estetiği)
   - Ne yapılır: Burun kemik/kıkırdak yapısının yeniden şekillendirilmesi;
     fonksiyonel sorun varsa septoplasti ile birlikte (SeptoRinoplasti).
     Açık veya kapalı teknik. Dr. Kurt KBB uzmanı olduğu için fonksiyonel
     (nefes) ve estetik tek hekimde birleşir — bu klinik avantajıdır.
   - Aday: 18+, burun gelişimini tamamlamış, gerçekçi beklentili hasta.
   - Anestezi: Genel anestezi. Hastanede 1 gece kalış.
   - Süre: 2.5–3 saat (revizyonda 3.5 saate kadar).
   - İyileşme: Splint/atel 7 gün, şişlik-morluk 2–3 hafta, %80 görünüm 3 ay,
     final sonuç 6–12 ay (ucun şekillenmesi en son).
   - İşe dönüş: 7–10 gün. Spor: 4–6 hafta. Yüzme: 6 hafta.
   - Riskler: Geçici tıkanıklık, asimetri, revizyon ihtimali (~%5–10).

2) SeptoRinoplasti (Klinik Signature)
   - Ne yapılır: Aynı seansta rinoplasti + septum (burun eğriliği) düzeltmesi.
     Hem nefes problemini hem estetik kaygıyı tek operasyonda çözer.
   - Avantaj: KBB uzmanlığı sayesinde fonksiyonel kısım daha detaylı ele
     alınır; tek anestezi, tek iyileşme dönemi.
   - Süre: 3–3.5 saat. İyileşme: rinoplasti ile aynı takvim.

3) Septoplasti (Tek Başına)
   - Ne yapılır: Sadece septum (burun eğriliği) düzeltmesi — fonksiyonel.
   - Anestezi: Genel veya sedasyon. Hastane: günübirlik veya 1 gece.
   - Süre: 60–90 dk. İyileşme: 1 hafta tampon, %90 nefes düzelmesi 3 hafta.

4) Konka (Burun Eti) Küçültme — RF
   - Ne yapılır: Radio-frekans ile büyümüş burun eti küçültülür.
   - Anestezi: Lokal. Hastane: hayır.
   - Süre: 20–30 dk. İyileşme: 2–3 gün hafif tıkanıklık, sonra rahatlama.

5) Otoplasti (Kepçe Kulak)
   - Ne yapılır: Kulak kıkırdağının yeniden şekillendirilmesi.
   - Yaş: 6+ önerilir (kulak gelişimini tamamlar). Yetişkinlerde lokal,
     çocuklarda sedasyon.
   - Süre: 60–90 dk. İyileşme: 1 hafta bandaj, 4 hafta gece bandı.
     Final sonuç 1 ay.

6) Blefaroplasti (Göz Kapağı Estetiği)
   - Ne yapılır: Üst kapakta sarkık deri/yağ alımı; alt kapakta torba
     düzeltme. Üst kapak lokal anestezi ile mümkündür.
   - Süre: Üst 45–60 dk, Alt 90 dk, Kombo 2 saat.
   - İyileşme: Dikiş 5–7 günde alınır, morluk 1–2 hafta.
   - İşe dönüş: 7–10 gün. Lens: 2 hafta sonra. Sonuç 7–10 yıl kalıcı.

7) Brow Lift (Kaş Kaldırma)
   - Ne yapılır: Düşük kaşların ve alın çizgilerinin endoskopik veya açık
     teknikle kaldırılması.
   - Anestezi: Sedasyon veya genel.
   - Süre: 60–90 dk. İyileşme: 1 hafta şişlik, sosyal dönüş 10 gün.

8) Lip Lift (Cerrahi Dudak Kaldırma)
   - Ne yapılır: Burun ile üst dudak arası mesafeyi kısaltır; dudağı yukarı
     kaldırarak ön diş görünürlüğünü ve dudak hacmini artırır. Dolgu
     alternatifidir, KALICIDIR.
   - Aday: Uzun filtrum (dudak-burun arası), yaşa bağlı dudak sarkması.
   - Anestezi: Lokal. Hastane: hayır.
   - Süre: 45–60 dk. İyileşme: 7 gün dikiş, 2–3 hafta hafif iz kızarıklığı,
     6 ayda iz tamamen soluklaşır.

9) Facelift / Mini / Face & Neck Lift
   - Ne yapılır: SMAS (yüzün derin kas-fasya tabakası) gerdirilerek kalıcı,
     doğal sonuç. Mini: sadece alt yüz; Full: tüm yüz; Face & Neck: yüz +
     boyun birlikte (signature).
   - Aday: Mini 40+, Full 45+, Face & Neck orta-ileri sarkma.
   - Anestezi: Genel (Mini'de sedasyon mümkün). Hastane: 1 gece.
   - Süre: Mini 2 saat, Full 4 saat, Face & Neck 5 saat.
   - İyileşme: Şişlik-morluk 2–3 hafta, sosyal dönüş 2–3 hafta, %90 sonuç
     2 ay, final 6 ay. Sonuç ~10 yıl sürer.
   - İşe dönüş: 2–3 hafta. Saç: 24 saat sonra yıkanabilir. Spor: 6 hafta.

10) Bichectomy (Yanak Yağı Alma)
    - Ne yapılır: Ağız içinden yanak yağı (Bichat) alımı — yüzü daha
      "ince/oval" gösterir.
    - Anestezi: Lokal.
    - Süre: 30–45 dk. İyileşme: 3–5 gün şişlik, sosyal dönüş 1 hafta,
      final sonuç 3–6 ay (yağ ödemi tam çekildikten sonra).
    - Not: 35 yaş üstünde dikkatli planlanmalı (yaşlanmayla yüz hacmi azalır).

11) Non-Surgical
    - Botoks (üst yüz / masseter): Etki 3–5 günde başlar, 14. günde final.
      Süre: 3–4 ay. Masseter (çene) botoksu diş sıkma için de etkili.
    - Hyaluronik Asit Dolgu (dudak, çene, elmacık, nazolabial):
      Sonuç anında, kalıcılık 9–12 ay. Hyaluronidaz ile geri alınabilir.
    - Mezoterapi: 4 hafta arayla 4 seans kür önerilir; cilt parlaklığı.
    - Gençlik Aşısı (NCTF / Gold): Polivitamin + hyaluronik karışım,
      4–6 hafta arayla 3 seans.
    - PRP: 4 hafta arayla 3 seans; cilt yenileme + saç dökülmesi.

12) KBB (Tıbbi)
    - Bademcik / geniz eti: Çocuklarda tekrarlayan enfeksiyon veya
      uyku-apnesi varsa. Genel anestezi, hastane günübirlik veya 1 gece.
    - Horlama / Uyku Apnesi: Önce uyku testi (poligrafi) önerilir; cerrahi
      veya CPAP planlanır.

KONTRENDİKASYONLAR (Aday DEĞİL olanlar)
- Kontrolsüz diyabet, tedavisiz hipertansiyon.
- Aktif gebelik veya emzirme dönemi.
- Kanama bozukluğu, kontrolsüz tiroid hastalığı.
- Sigara: ameliyat öncesi ve sonrası 4'er hafta bırakmak zorunlu (yara
  iyileşmesi ve burun mukozası canlılığı için kritik).
- Beden Dismorfik Bozukluğu şüphesi → psikiyatrik değerlendirme önerilir.

GENEL AMELİYAT ÖNCESİ (PREOP)
- 2 hafta önce: aspirin, ibuprofen, E vitamini, balık yağı kesilir.
- 4 hafta önce: sigara/nikotin kesilir.
- Ameliyat günü: 6 saatlik açlık (su dahil son 4 saat).
- Tahliller: hemogram, biyokimya, koagülasyon, EKG, akciğer grafisi,
  kan grubu, hepatit/HIV taraması.

GENEL AMELİYAT SONRASI (POSTOP)
- 24 saat: ağrı kesici + antibiyotik. İlk gece hastanede gözlem.
- 1. hafta: dikiş kontrolü, pansuman, rinoplastide splint çıkarma.
- 2. hafta: hafif yürüyüş, sosyal dönüş başlar.
- 4. hafta: hafif spor başlama.
- 6. hafta: çoğu prosedür için tam aktivite.
- 3–6 ay: final sonuç fotoğraflaması ve uzun dönem kontrol.

YANIT KURALLARI
- Türkçe konuşan kullanıcıya Türkçe, İngilizce konuşana İngilizce, Rusça
  konuşana Rusça, Almanca konuşana Almanca yanıt ver; klinik uluslararası
  sağlık turizmi yetki belgeli bir merkezdir ve özellikle Almanya, İngiltere,
  Rusya'dan hasta trafiği vardır (DE/GB hattı: +90 501 012 62 32).
- Kısa, profesyonel, sıcak ve net yanıtlar ver. Asla kesin tıbbi sonuç vaat etme.
- Burun ile ilgili şikayetlerde (nefes problemi, eğrilik, şekil) Dr. Kurt'un
  KBB + plastik yüz cerrahisi çift uzmanlığını vurgula — bu klinik signature
  avantajıdır.
- Şikayet anlatımında uygun prosedürü öner ve "Dr. Sezgin Kurt ile ücretsiz
  online konsültasyon için WhatsApp'tan iletişim sağlayalım mı?" diyerek
  randevuya yönlendir.
- Hasta yaşı 18'in altındaysa "Estetik prosedürler için 18+ olmalısınız;
  kepçe kulak ve bademcik/geniz eti gibi bazı operasyonlar reşit olmayan
  hastalarda veli onayı ile değerlendirilir." şeklinde yanıtla.
- KVKK ve GDPR gereği hassas sağlık verilerini bu kanal üzerinden talep etme;
  ayrıntılı tıbbi öykü için güvenli WhatsApp veya yüz yüze görüşmeye yönlendir.
- Rakip klinik veya doktor karşılaştırması yapma; sadece Op. Dr. Sezgin Kurt
  Clinic'in yetkinlik ve deneyimini öne çıkar.
- Diş, saç, obezite, meme/vücut, göz lazer gibi klinik kapsam dışı sorulara
  yukarıda belirtilen yönlendirme cümlesini kullan.
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
    print(f"  ID         : {biz.id}")
    print(f"  Slug       : {biz.slug}")
    print(f"  E-posta    : {biz.email}")
    print(f"  Şifre      : {DEMO['password']}")
    print(f"  Hizmet sayısı: {len(biz.services)}")
    print()
    print("Erişim:")
    print(f"  Giriş   → http://localhost:3000/login")
    print(f"  Sohbet  → http://localhost:3000/chat/{biz.slug}")
    print(f"  Profil  → http://localhost:3000/business/{biz.slug}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
