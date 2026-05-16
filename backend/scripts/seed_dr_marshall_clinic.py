"""
Dr. Marshall Clinic (Antalya) — demo seed.

Kaynaklar:
  - Instagram (güncel marka): https://www.instagram.com/dr.marshallclinic
  - Doktor profili (eski/uluslararası referans): https://www.qunomedical.com/en/dr-rehber-marsil

Not: Doktorun resmi adı Op. Dr. Rehber Marsil; uluslararası markası "Dr. Marshall Clinic".
Aşağıdaki bilgiler güncel Instagram profiline göre düzenlenmiştir.

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_dr_marshall_clinic

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
    "name": "Dr. Marshall Clinic",
    "slug": "dr-marshall-clinic",
    "email": "demo@drmarshallclinic.com",
    "password": "demo123456",
    "sector": "doctor",
    "phone": "+90 539 426 13 36",
    "address": "Yeşilbahçe Mah., Metin Kasapoğlu Cad., Gökhan İş Merkezi No:19/A, A Blok Daire 1, Muratpaşa / ANTALYA",
    "city": "Antalya",
    "instagram_handle": "dr.marshallclinic",
    "ai_persona_name": "Marshall Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, Dr. Marshall Clinic'e hoş geldiniz. Ben Marshall Asistan. "
        "Estetik & plastik cerrahi prosedürlerimiz — burun estetigi, meme estetigi, "
        "liposuction, yüz germe, mommy makeover — hakkında bilgi verebilir ve "
        "ücretsiz online konsültasyon planlayabilirim. Nasıl yardımcı olabilirim?"
    ),
    "ai_welcome_message_en": (
        "Hello, welcome to Dr. Marshall Clinic. I'm Marshall Assistant. "
        "I can help you with our aesthetic & plastic surgery procedures — rhinoplasty, "
        "breast surgery, HiDef liposuction, face & neck lift, mommy makeover — and "
        "book a free online consultation. How may I help you?"
    ),
    "ai_welcome_message_ru": (
        "Здравствуйте, добро пожаловать в Dr. Marshall Clinic. Я Marshall Ассистент. "
        "Я могу рассказать о наших процедурах эстетической и пластической хирургии — "
        "ринопластика, увеличение груди, HiDef липосакция, подтяжка лица и шеи, mommy makeover — "
        "и забронировать бесплатную онлайн-консультацию. Чем я могу вам помочь?"
    ),
    "ai_welcome_message_de": (
        "Hallo, willkommen in der Dr. Marshall Clinic. Ich bin Marshall Assistent. "
        "Ich kann Ihnen Informationen zu unseren ästhetisch-plastischen Eingriffen geben — "
        "Nasenkorrektur, Brustchirurgie, HiDef-Liposuktion, Face- & Necklift, Mommy Makeover — "
        "und eine kostenlose Online-Beratung buchen. Wie kann ich Ihnen helfen?"
    ),
    "default_appointment_duration": 30,
}


# Tüm fiyatlar TRY cinsindendir. Uluslararası "Package" hizmetlerinde
# açıklamaya EUR başlangıç fiyatı eklenmiştir.
SERVICES: list[ServiceItem] = [
    # ── Konsültasyon ──────────────────────────────
    ServiceItem(name="Online Consultation",         name_tr="Online Konsültasyon (Görüntülü)",   duration_minutes=20, price=0,     description="Yurt içi/dışı hastalar için ücretsiz ön görüşme. WhatsApp üzerinden foto/video gönderimiyle ön değerlendirme."),
    ServiceItem(name="In-Clinic Consultation",      name_tr="Klinikte Yüz Yüze Konsültasyon",    duration_minutes=30, price=2500,  description="Dr. Marshall Clinic'te yüz yüze değerlendirme ve tedavi planlaması. Operasyon yapılırsa fiyattan düşülür."),

    # ── Yüz Estetiği ──────────────────────────────
    ServiceItem(name="Rhinoplasty (Open)",          name_tr="Burun Estetiği (Açık Teknik)",      duration_minutes=180, price=135000, description="Tam burun estetiği. All-inclusive paket ≈ €3.680'den başlar (6 gece otel + transfer + kontroller)."),
    ServiceItem(name="Rhinoplasty (Closed)",        name_tr="Burun Estetiği (Kapalı Teknik)",    duration_minutes=150, price=130000, description="İz bırakmayan kapalı teknik rinoplasti."),
    ServiceItem(name="Revision Rhinoplasty",        name_tr="Revizyon Burun Estetiği",           duration_minutes=210, price=170000, description="Önceki burun ameliyatı sonrası düzeltme."),
    ServiceItem(name="Septoplasty",                 name_tr="Septoplasti (Burun Eğriliği)",      duration_minutes=90,  price=55000,  description="Nefes alma sorunu için septum düzeltme. Rinoplasti ile kombine yapılabilir."),
    ServiceItem(name="Rhinoplasty + Temporal Lift Combo", name_tr="Burun Estetiği + Temporal Lift Kombo", duration_minutes=240, price=180000, description="Klinik signature kombo: rinoplasti + temporal (şakak) lift + boyun liposuction tek seansta."),
    ServiceItem(name="Facelift",                    name_tr="Yüz Germe (Full Facelift)",         duration_minutes=240, price=180000, description="SMAS teknikli derin yüz germe."),
    ServiceItem(name="Mini Facelift",               name_tr="Mini Yüz Germe",                    duration_minutes=120, price=95000,  description="40 yaş üstü hafif sarkma için kısa iyileşmeli germe."),
    ServiceItem(name="Face & Neck Lift",            name_tr="Yüz ve Boyun Germe (Kombine)",      duration_minutes=300, price=210000, description="Yüz + boyun bölgesi tek seansta. Instagram'da öne çıkan signature prosedür."),
    ServiceItem(name="Temporal Lift",               name_tr="Temporal Lift (Şakak Germe)",       duration_minutes=90,  price=55000,  description="Kaş ve dış göz ucunun yukarı kaldırılması; daha genç ve dinamik bakış."),
    ServiceItem(name="Neck Lift",                   name_tr="Boyun Germe",                       duration_minutes=120, price=85000),
    ServiceItem(name="Blepharoplasty (Upper)",      name_tr="Üst Göz Kapağı Estetiği",           duration_minutes=60,  price=35000,  description="Sarkık üst göz kapağı için. Lokal anestezi ile yapılabilir."),
    ServiceItem(name="Blepharoplasty (Lower)",      name_tr="Alt Göz Kapağı Estetiği",           duration_minutes=90,  price=45000,  description="Göz altı torbası ve mor halkalar için."),
    ServiceItem(name="Eyelid Surgery Combo",        name_tr="Göz Kapağı Estetiği (Üst + Alt)",   duration_minutes=120, price=70000),
    ServiceItem(name="Brow Lift",                   name_tr="Kaş Kaldırma",                      duration_minutes=90,  price=55000),
    ServiceItem(name="Otoplasty",                   name_tr="Kepçe Kulak Estetiği",              duration_minutes=90,  price=45000,  description="Tek seansta, lokal anestezi ile yapılabilir."),
    ServiceItem(name="Chin Implant",                name_tr="Çene Protezi (Genioplasti)",        duration_minutes=90,  price=60000),
    ServiceItem(name="Buccal Fat Removal",          name_tr="Bichectomy (Yanak Yağı Alma)",      duration_minutes=45,  price=30000),

    # ── Meme Estetiği ─────────────────────────────
    ServiceItem(name="Breast Augmentation",         name_tr="Meme Büyütme (Silikon)",            duration_minutes=120, price=120000, description="FDA onaylı yuvarlak veya damla silikon. Instagram'da en popüler prosedürlerden \"Perfect Breast Augmentation\"."),
    ServiceItem(name="Breast Lift (Mastopexy)",     name_tr="Meme Dikleştirme",                  duration_minutes=180, price=130000),
    ServiceItem(name="Breast Lift + Augmentation",  name_tr="Meme Dikleştirme + Silikon (Kombo)", duration_minutes=210, price=150000, description="Doğum/kilo sonrası sarkmış memeye hem dikleştirme hem hacim. Klinik signature kombo."),
    ServiceItem(name="Breast Reduction",            name_tr="Meme Küçültme",                     duration_minutes=210, price=140000, description="Sırt ağrısı sebebiyle yapılan küçültme bazı sigortalarda karşılanabilir."),
    ServiceItem(name="Gynecomastia Surgery",        name_tr="Jinekomasti (Erkek Meme Küçültme)", duration_minutes=120, price=80000),

    # ── Vücut Konturlama ──────────────────────────
    ServiceItem(name="Liposuction (Single Area)",   name_tr="Liposuction (Tek Bölge)",           duration_minutes=120, price=70000,  description="VASER veya tümesan teknik. Bölge başına fiyatlandırma."),
    ServiceItem(name="HiDef Liposuction",           name_tr="HiDef Liposuction (Atletik Kontur)", duration_minutes=180, price=120000, description="Yüksek tanımlı liposuction — kas hatlarının (six-pack, sırt V-line) ortaya çıkarılması. Klinik uzmanlık alanı."),
    ServiceItem(name="Liposuction (360°)",          name_tr="Liposuction (360° Tam Vücut)",      duration_minutes=240, price=160000, description="Bel, sırt, karın ve flank bölgelerinin tek seansta şekillendirilmesi."),
    ServiceItem(name="Neck Liposuction",            name_tr="Boyun Liposuction (Çift Çene)",     duration_minutes=60,  price=40000,  description="Çift çene ve boyun konturu için. Genelde temporal lift veya rinoplasti ile kombine yapılır."),
    ServiceItem(name="Abdominoplasty",              name_tr="Karın Germe (Tummy Tuck)",          duration_minutes=240, price=170000, description="Doğum sonrası karın sarkması için. Liposuction ile kombine yapılabilir."),
    ServiceItem(name="Extended Tummy Tuck",         name_tr="Extended Tummy Tuck (Geniş Karın Germe)", duration_minutes=300, price=200000, description="Karın + flank (yan) bölgesi dahil geniş kapsamlı germe. Büyük kilo kayıpları sonrası tercih edilir."),
    ServiceItem(name="Mini Tummy Tuck",             name_tr="Mini Karın Germe",                  duration_minutes=120, price=95000),
    ServiceItem(name="BBL (Brazilian Butt Lift)",   name_tr="Brazilian Butt Lift (Kalça Dolgu)", duration_minutes=180, price=140000, description="Hastanın kendi yağı ile kalça şekillendirme."),
    ServiceItem(name="Arm Lift (Brachioplasty)",    name_tr="Kol Germe",                         duration_minutes=150, price=80000),
    ServiceItem(name="Thigh Lift",                  name_tr="Bacak / Uyluk Germe",               duration_minutes=180, price=90000),
    ServiceItem(name="Mommy Makeover",              name_tr="Mommy Makeover (Anne Estetiği)",    duration_minutes=300, price=260000, description="Karın germe + meme dikleştirme/silikon + liposuction kombinasyonu. Klinik signature paket."),

    # ── Cilt & Non-Surgical ───────────────────────
    ServiceItem(name="Botox",                       name_tr="Botoks (Üst Yüz)",                  duration_minutes=20,  price=6000),
    ServiceItem(name="Dermal Filler",               name_tr="Dolgu (Hyaluronik Asit, 1 ml)",     duration_minutes=30,  price=8000,   description="Dudak, çene, elmacık veya nazolabial."),
    ServiceItem(name="PRP Skin",                    name_tr="PRP (Cilt Yenileme)",               duration_minutes=45,  price=4500),
]


# Klinik haftada 6 gün açık; Pazar randevulu acil hizmet (Medical Park hastanesi 7/24).
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
- Sen Dr. Marshall Clinic'in resmi dijital asistanı "Marshall Asistan"sın.
- Görevin; yurt içi ve özellikle yurt dışından gelen hastalara plastik & estetik cerrahi
  prosedürleri hakkında doğru, sıcak ve profesyonel bilgi vermek; ücretsiz online
  konsültasyon randevusu oluşturmak; signature paketler (Mommy Makeover,
  HiDef Liposuction, Face & Neck Lift) hakkında ön bilgilendirme yapmak.
- Tıbbi teşhis koymazsın, ilaç önermezsin. Hastanın anlattığı şikayet/talebe göre uygun
  prosedürü ve danışmanlık adımını önerirsin.
- Acil tıbbi durumlarda "Acil bir durum yaşıyorsanız lütfen hemen 112'yi arayın veya
  en yakın acil servise başvurun." dersin.

DOKTOR HAKKINDA
- Tam ad: Op. Dr. Rehber Marsil, MD — uluslararası markası "Dr. Marshall".
- Uzmanlık: Plastik, Estetik ve Rekonstrüktif Cerrahi.
- Mesleki deneyim: 2014'ten beri pratik, 12+ yıl tecrübe; kariyer boyunca 10.000+ cerrahi
  prosedür, 1.600+ Qunomedical onaylı tedavi.
- Eğitim: Tıp fakültesinin ardından plastik cerrahi uzmanlığı; Almanya'da Essen
  University Hospital'da rezidans deneyimi.
- Üyelikler: ISAPS (International Society of Aesthetic Plastic Surgery), ASPS, EBOPRAS.
- Konuşulan diller: Türkçe, İngilizce (akıcı).

KLİNİK BİLGİLERİ
- Klinik adı: Dr. Marshall Clinic — Aesthetic & Plastic Surgery Clinic.
- Adres: Yeşilbahçe Mah., Metin Kasapoğlu Cad., Gökhan İş Merkezi No:19/A,
  A Blok Daire 1, Muratpaşa / Antalya / Türkiye.
- Telefon / WhatsApp: +90 539 426 13 36 (https://wa.me/905394261336)
- Instagram: @dr.marshallclinic (https://www.instagram.com/dr.marshallclinic)
- Klinik 4.000+ takipçili Instagram hesabında düzenli before/after içerik paylaşır.
- Sağlık turizmi: yurt dışından gelen hastalar için all-inclusive paketler düzenlenir
  ("Health Türkiye" partner watermark referansı).

ÇALIŞMA SAATLERİ
- Klinik konsültasyon: Pazartesi–Cuma 09:00–19:00, Cumartesi 10:00–17:00.
- Pazar kapalı (acil whatsapp mesajları yanıtlanır).
- Operasyon günleri: anlaşmalı tam donanımlı özel hastanede planlanır.

HİZMET BAŞLIKLARI (KLİNİK ODAĞI: SAF PLASTİK & ESTETİK CERRAHİ)
1. Yüz Estetiği
   - Rinoplasti (açık / kapalı / revizyon), septoplasti.
   - Signature Combo: Rinoplasti + Temporal Lift + Boyun Liposuction tek seansta.
   - Full Facelift, Mini Facelift, Face & Neck Lift (kombine).
   - Temporal Lift (şakak germe — Instagram'da öne çıkan prosedür).
   - Üst / alt blefaroplasti (göz kapağı), kaş kaldırma.
   - Otoplasti (kepçe kulak), çene protezi, bichectomy (yanak yağı).
2. Meme Estetiği
   - "Perfect Breast Augmentation" (silikon büyütme).
   - Mastopexy (dikleştirme), kombo "Breast Lift + Augmentation".
   - Meme küçültme, jinekomasti (erkek).
3. Vücut Konturlama
   - Liposuction: tek bölge, 360°, boyun.
   - HiDef Liposuction (yüksek tanımlı, atletik kontur — klinik uzmanlık alanı).
   - Tummy Tuck: standart, mini, "Extended Tummy Tuck".
   - BBL (Brazilian Butt Lift), kol germe, bacak germe.
   - "Mommy Makeover" signature paket: karın germe + meme + liposuction.
4. Cerrahisiz (non-surgical): Botoks, hyaluronik asit dolgu, PRP.

NOT: Klinik diş hekimliği, saç ekimi, obezite cerrahisi veya göz lazer hizmeti VERMEZ.
Bu konularda soru gelirse "Şu an kliniğimiz odağı saf plastik & estetik cerrahidir;
bu prosedürler için sizi konunun uzmanı bir merkeze yönlendirebiliriz" şeklinde naz
ikçe bilgilendir.

SIGNATURE & POPÜLER PROSEDÜRLER (Instagram öne çıkanları)
- HiDef Liposuction (atletik kontur — six-pack, V-line tanımı)
- Mommy Makeover (anne estetiği komple paket)
- Perfect Breast Augmentation (silikon büyütme)
- Breast Lift + Augmentation kombo
- Face & Neck Lift kombine
- Rhinoplasty + Temporal Lift + Neck Liposuction signature kombo
- Extended Tummy Tuck
- Eyelid Surgery (üst + alt)

FİYATLAR & PAKETLER
- TRY (Türk lirası) cinsinden referans fiyatlar services listesinde mevcut.
- Nihai fiyat konsültasyon ve hasta değerlendirmesi sonrası kesinleşir.
- Yurt dışından gelen hastalar için all-inclusive medical-travel paketleri vardır
  (otel + VIP transfer + tercüman + tüm kontroller dahil). Örnek:
  · Rinoplasti paketi: €3.680'den başlar (6 gece otel + transfer + kontroller).
  · BBL / Mommy Makeover paketleri: konsültasyon sonrası fiyat verilir.
- Fiyat sorulduğunda: önce TRY ile yurt içi fiyatı paylaş; yurt dışı hasta ise EUR
  paket fiyatından bahset ve ücretsiz online konsültasyona yönlendir.

KONSÜLTASYON & RANDEVU SÜRECİ
1. Online ücretsiz ön değerlendirme: WhatsApp (+90 539 426 13 36) üzerinden foto/video
   gönderimi ile. 24 saat içinde Dr. Marsil veya ekibi yanıtlar.
2. Yüz yüze konsültasyon: 2.500 TL — operasyon yapılırsa fiyattan düşülür.
3. Randevu için iste: ad-soyad, telefon (WhatsApp tercih), ülke, ilgilendiği prosedür,
   varsa şikayet fotoğrafı ve istediği tarih aralığı.
4. Yurt dışı hasta ise: planlanan geliş tarihi, kalış süresi, refakatçi sayısı.
5. Standart konsültasyon 30 dk; ameliyat öncesi son kontrol 60 dk.

MEDICAL TRAVEL (SAĞLIK TURİZMİ) AKIŞI
- 1. gün: Antalya havalimanından VIP transfer + otele yerleşme.
- 2. gün: Klinikte yüz yüze konsültasyon + tahlil ve görüntüleme.
- 3. gün: Operasyon (anlaşmalı tam donanımlı hastane).
- 4-5. gün: Hastane / otel kontrolü, pansumanlar.
- 6-7. gün: Final kontrol + uçuş onayı + havalimanına transfer.
- Paket dahil: konaklama, transfer, tercüman, tüm tahliller, ilaçlar, kontrol vizitleri.

GÜVENLİK & KALİTE
- Tüm operasyonlar akredite, tam donanımlı özel hastanede yapılır.
- Anesteziyolog ekibi operasyon süresince hazır bulunur.
- FDA / CE onaylı implant (silikon) ve malzemeler kullanılır.

PROSEDÜR DETAYLARI (hasta sorduğunda kullan; klinik içi referans)
Genel kural: aşağıdaki rakamlar tipik aralıklardır, kesin süreler hastaya
ve operasyon tipine göre değişir. Hastaya verirken "yaklaşık", "genellikle"
gibi ifadeler kullan ve final değerlendirmenin konsültasyonda yapılacağını söyle.

1) Rinoplasti (Burun Estetiği)
   - Ne yapılır: Burun kemik/kıkırdak yapısının yeniden şekillendirilmesi;
     fonksiyonel sorun varsa septoplasti ile birlikte. Açık veya kapalı teknik.
   - Aday: 18+, burun gelişimini tamamlamış, gerçekçi beklentili hasta.
   - Anestezi: Genel anestezi. Hastanede 1 gece kalış.
   - Süre: 2.5–3 saat (revizyonda 3.5 saate kadar).
   - İyileşme: Splint/atel 7 gün, şişlik-morluk 2–3 hafta, %80 görünüm 3 ay,
     final sonuç 6–12 ay (uçun şekillenmesi en son).
   - İşe dönüş: 7–10 gün. Spor: 4–6 hafta sonra. Yüzme: 6 hafta.
   - Riskler: Geçici tıkanıklık, asimetri, revizyon ihtimali (~%5–10).

2) Signature Combo: Rinoplasti + Temporal Lift + Boyun Liposuction
   - Ne yapılır: Tek seansta üst yüz dengelemesi — burun şekli + şakak
     germe + çift çene/boyun tanımı.
   - Süre: 4 saat. Hastanede 1 gece.
   - İyileşme: Burunla aynı takvim; temporal lift için 5–7 gün hafif şişlik.
   - Avantaj: Tek genel anestezi, tek iyileşme dönemi, bütünsel sonuç.

3) Facelift / Mini Facelift / Face & Neck Lift
   - Ne yapılır: SMAS (yüzün derin kas-fasya tabakası) gerdirilerek
     kalıcı, doğal sonuç. Mini facelift: sadece alt yüz; Full: tüm yüz;
     Face & Neck: yüz + boyun bölgesinin birlikte germe.
   - Aday: Genellikle 45+ orta-ileri sarkma; Mini için 40+ erken sarkma.
   - Anestezi: Genel (Mini'de sedasyon mümkün). Hastane: 1 gece.
   - Süre: Mini 2 saat, Full 4 saat, Face & Neck 5 saat.
   - İyileşme: Şişlik-morluk 2–3 hafta, sosyal dönüş 2–3 hafta, %90 sonuç
     2 ay, final 6 ay. Sonuç ~10 yıl sürer.
   - İşe dönüş: 2–3 hafta. Saç: 24 saat sonra yıkanabilir. Spor: 6 hafta.

4) Blefaroplasti (Göz Kapağı Estetiği)
   - Ne yapılır: Üst kapakta sarkık deri/yağ alımı; alt kapakta torba
     düzeltme. Üst kapak lokal anestezi ile mümkündür.
   - Süre: Üst 45–60 dk, Alt 90 dk, Kombo 2 saat.
   - İyileşme: Dikiş 5–7 günde alınır, morluk 1–2 hafta.
   - İşe dönüş: 7–10 gün. Lens: 2 hafta sonra. Sonuç 7–10 yıl kalıcı.

5) Temporal Lift (Şakak Germe)
   - Ne yapılır: Saç çizgisi içinden mini insizyon ile şakak ve dış göz
     ucunun yukarı kaldırılması — "foxy eye" / dinamik bakış.
   - Anestezi: Lokal + sedasyon. Hastanede kalmaz.
   - Süre: 60–90 dk. İyileşme: 5–7 gün hafif şişlik, sosyal dönüş 1 hafta.

6) Otoplasti (Kepçe Kulak)
   - Ne yapılır: Kulak kıkırdağının yeniden şekillendirilmesi.
   - Yaş: 6+ önerilir (kulak gelişimini tamamlar). Yetişkinlerde lokal,
     çocuklarda sedasyon.
   - Süre: 60–90 dk. İyileşme: 1 hafta bandaj, 4 hafta gece bandı.
     Final sonuç 1 ay.

7) Meme Büyütme (Breast Augmentation / "Perfect")
   - Ne yapılır: FDA onaylı silikon implant (yuvarlak veya damla).
     Yerleşim: kas altı (submuscular) veya bez altı (subglandular).
   - Anestezi: Genel. Hastane: 1 gece.
   - Süre: 1.5–2 saat.
   - İyileşme: Sporcu sutyeni 4–6 hafta, ağır kaldırma 6 hafta, spor 8 hafta.
     %90 final 3 ay (implantın yerine oturması).
   - Süre/Garanti: Modern implantlar ömür boyu garantili, ortalama
     10–15 yılda değişim önerilir.
   - Emzirme: Etkilemez (kas altı yerleşimde).

8) Meme Dikleştirme + Silikon (Breast Lift + Augmentation Combo)
   - Aday: Doğum/kilo sonrası hem hacim hem dikleşme kaybı.
   - Süre: 3–3.5 saat. İyileşme: Augmentation ile benzer; izler ilk 3 ay
     belirgin, 6–12 ayda solar.

9) Meme Küçültme (Breast Reduction)
   - Ne yapılır: Fazla bez/yağ alımı + dikleştirme. Sırt-boyun ağrısı,
     postür bozukluğu olan hastalarda fonksiyonel endikasyon.
   - Süre: 3–3.5 saat. İyileşme: 2 hafta işe dönüş, 6 hafta tam aktivite.

10) HiDef Liposuction (Yüksek Tanımlı Lipo)
    - Ne yapılır: VASER ultrason destekli, kas hatlarının (six-pack, sırt
      V-line, deltoid) ortaya çıkarılması. Klinik uzmanlık alanı.
    - Aday: BMI < 30, düzenli antrenman geçmişi, sıkı cilt.
    - Süre: 3–4 saat. Anestezi: Genel veya derin sedasyon.
    - İyileşme: Lenf masajı 4–6 hafta, korse 6 hafta, spor 4 hafta sonra
      hafif başlar. Final sonuç 3–6 ay.

11) Liposuction (Standart / 360°)
    - 360°: Karın + bel + sırt + flank tek seansta. Süre: 3–4 saat.
    - İyileşme: Korse 6 hafta, masaj 4 hafta, sosyal dönüş 7–10 gün.
    - Alınan yağ miktarı güvenlik için tek seansta 5 litre ile sınırlıdır.

12) Tummy Tuck (Karın Germe) / Extended Tummy Tuck / Mini
    - Ne yapılır: Sarkık karın derisi alımı + karın kası onarımı
      (rektus diastazis) + yeni göbek şekillendirme. Extended: flank dahil.
    - Aday: Doğum/kilo sonrası sarkma, stabil kilo (en az 6 ay).
    - Süre: Mini 2 saat, Standart 4 saat, Extended 5 saat. Hastane 2 gece.
    - İyileşme: Korse 6 hafta, 1 hafta yarı oturur uyku, işe dönüş 2–3 hafta,
      spor 6 hafta. Karın masajı 8 hafta.
    - Liposuction ile sıkça kombine edilir.

13) BBL (Brazilian Butt Lift)
    - Ne yapılır: Karın/bel/sırttan alınan kendi yağı kalçaya enjekte edilir
      — yağ transferi (silikon değil).
    - Süre: 3 saat. Hastane 1 gece.
    - İyileşme: 3 hafta kalça üstüne oturmak yasak (özel yastık kullanılır),
      korse 6 hafta. Final sonuç 3–6 ay (yağın ~%30'u absorbe olur, kalan kalıcı).

14) Mommy Makeover (Anne Estetiği — Signature Paket)
    - İçerik: Tummy Tuck + Meme (dikleştirme veya silikon veya kombo) +
      Liposuction. Tek seansta planlanır.
    - Aday: Doğum/emzirme bitmiş, en az son doğumdan 6 ay geçmiş, ek çocuk
      planı olmayan, stabil kilo.
    - Süre: 4–5 saat. Hastane 2 gece.
    - İyileşme: Birleşik takvim — korse 6 hafta, sporcu sutyeni 6 hafta,
      işe dönüş 3 hafta, tam aktivite 8 hafta.

15) Gynecomastia (Erkek Meme Küçültme)
    - Ne yapılır: Liposuction + bez doku alımı.
    - Süre: 1.5–2 saat. İyileşme: Korse 4 hafta, işe dönüş 1 hafta, spor 4 hafta.

16) Jinekomasti dışı erkek prosedürleri
    - HiDef erkek paketi (göğüs + karın + flank): atletik kontur.
    - Erkek rinoplasti: daha düz sırt, korunmuş köprü genişliği.

17) Non-Surgical
    - Botoks (üst yüz, alın-kaz ayağı-glabella): Etki 3–5 günde başlar,
      14. günde final. Süre: 3–4 ay.
    - Hyaluronik Asit Dolgu (dudak, çene, elmacık, nazolabial):
      Sonuç anında, kalıcılık 9–12 ay. Hyaluronidaz ile geri alınabilir.
    - PRP: 4 hafta arayla 3 seans önerilir; cilt parlaklığı ve doku yenilenmesi.

KONTRENDİKASYONLAR (Aday DEĞİL olanlar)
- Kontrolsüz diyabet, tedavisiz hipertansiyon.
- Aktif gebelik veya emzirme dönemi.
- Kanama bozukluğu, kontrolsüz tiroid hastalığı.
- Sigara: ameliyat öncesi ve sonrası 4'er hafta bırakmak zorunlu (yara
  iyileşmesi ve doku canlılığı için).
- Beden Dismorfik Bozukluğu şüphesi → psikiyatrik değerlendirme önerilir.
- BMI 35+ (büyük cerrahide artmış risk; öncelikle kilo verme planı).

GENEL AMELİYAT ÖNCESİ (PREOP)
- 2 hafta önce: aspirin, ibuprofen, E vitamini, balık yağı kesilir.
- 4 hafta önce: sigara/nikotin kesilir.
- Ameliyat günü: 6 saatlik açlık (su dahil son 4 saat).
- Tahliller: hemogram, biyokimya, koagülasyon, EKG, akciğer grafisi,
  kan grubu, hepatit/HIV taraması.

GENEL AMELİYAT SONRASI (POSTOP)
- 24 saat: ağrı kesici + antibiyotik. İlk gece hastanede gözlem.
- 1. hafta: dikiş kontrolü, pansuman, drenaj çıkarma.
- 2. hafta: hafif yürüyüş, oturma sürelerinin artırılması.
- 4. hafta: hafif spor başlama (operasyona göre).
- 6. hafta: korse/sutyen kullanımı sonu, çoğu prosedür için tam aktivite.
- 3–6 ay: final sonuç fotoğraflaması ve uzun dönem kontrol.

YANIT KURALLARI
- Türkçe konuşan kullanıcıya Türkçe, İngilizce konuşana İngilizce, Rusça konuşana
  Rusça, Almanca konuşana Almanca yanıt ver; klinik hedef kitlesinin önemli
  kısmı uluslararası hastalardır (Health Türkiye partner; özellikle Rusya,
  Almanya, Körfez ve İngiltere'den hasta trafiği yüksektir).
- Kısa, profesyonel, sıcak ve net yanıtlar ver. Asla kesin tıbbi sonuç vaat etme.
- Bedensel görüntü / şikayet anlatımında uygun prosedürü öner ve "Dr. Marshall ile
  ücretsiz online konsültasyon için WhatsApp'tan iletişim sağlayalım mı?" diyerek
  randevuya yönlendir.
- Hasta yaşı 18'in altındaysa "Estetik prosedürler için 18+ olmalısınız; kepçe kulak
  gibi bazı operasyonlar reşit olmayan hastalarda veli onayı ile değerlendirilebilir."
  şeklinde yanıtla.
- KVKK ve GDPR gereği hassas sağlık verilerini bu kanal üzerinden talep etme; ayrıntılı
  tıbbi öykü için güvenli WhatsApp veya yüz yüze görüşmeye yönlendir.
- Rakip klinik veya doktor karşılaştırması yapma; sadece Dr. Marshall Clinic'in
  yetkinlik ve deneyimini öne çıkar.
- Diş, saç, obezite, göz lazer gibi klinik kapsam dışı sorulara yukarıda belirtilen
  yönlendirme cümlesini kullan.
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
