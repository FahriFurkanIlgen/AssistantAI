"""
Akdeniz Şifa Hastanesi — demo seed.

Kullanım (backend/ klasöründen):
    .\venv\Scripts\python.exe -m scripts.seed_akdenizsifa

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
    "name": "Özel Akdeniz Şifa Hastanesi",
    "slug": "akdeniz-sifa",
    "email": "demo@akdenizsifa.com",
    "password": "demo123456",
    "sector": "doctor",
    "phone": "444 7 606",
    "address": "Kuzeyyaka Mahallesi Yeşilırmak Caddesi No: 367 Varsak Köprüsü Kepez/ANTALYA",
    "city": "Antalya",
    "instagram_handle": "ozelakdenizsifahastanesi",
    "ai_persona_name": "Şifa Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, Özel Akdeniz Şifa Hastanesi'ne hoş geldiniz. Ben Şifa Asistan. "
        "Bölümlerimiz, doktorlarımız, hizmetlerimiz veya randevu için yardımcı olabilirim. "
        "Nasıl destek olabilirim?"
    ),
    "ai_welcome_message_en": (
        "Hello, welcome to Akdeniz Şifa Hospital. I'm Şifa Assistant. "
        "I can help you with our departments, doctors, services or booking an appointment. "
        "How may I help you?"
    ),
    "default_appointment_duration": 20,
}


SERVICES: list[ServiceItem] = [
    # Genel muayene
    ServiceItem(name="General Examination", name_tr="Genel Muayene", duration_minutes=20, price=750, description="Tüm bölümler için standart poliklinik muayenesi."),
    # Acil
    ServiceItem(name="Emergency Service",   name_tr="Acil Servis (7/24)", duration_minutes=30, price=0, description="7 gün 24 saat hizmet veren acil servis. Triajla doğrudan müdahale."),

    # Cerrahi & Tıbbi bölümler
    ServiceItem(name="Cardiology",                 name_tr="Kardiyoloji",                       duration_minutes=30, price=900,  description="EKG, EKO, efor testi, holter."),
    ServiceItem(name="Cardiovascular Surgery",     name_tr="Kalp ve Damar Cerrahisi",           duration_minutes=30, price=1200, description="By-pass, kapak cerrahisi, varis tedavisi."),
    ServiceItem(name="Internal Medicine",          name_tr="İç Hastalıkları (Dahiliye)",        duration_minutes=20, price=750),
    ServiceItem(name="Pediatrics",                 name_tr="Çocuk Sağlığı ve Hastalıkları",     duration_minutes=20, price=750),
    ServiceItem(name="Obstetrics & Gynecology",    name_tr="Kadın Hastalıkları ve Doğum",       duration_minutes=30, price=900,  description="Gebelik takibi, USG, jinekoloji."),
    ServiceItem(name="General Surgery",            name_tr="Genel Cerrahi",                     duration_minutes=30, price=900),
    ServiceItem(name="Orthopedics & Traumatology", name_tr="Ortopedi ve Travmatoloji",          duration_minutes=30, price=900),
    ServiceItem(name="Neurosurgery",               name_tr="Beyin ve Sinir Cerrahisi",          duration_minutes=30, price=1200, description="Bel ve boyun fıtığı, beyin cerrahisi."),
    ServiceItem(name="Neurology",                  name_tr="Nöroloji",                          duration_minutes=30, price=900),
    ServiceItem(name="Ophthalmology",              name_tr="Göz Hastalıkları",                  duration_minutes=20, price=850,  description="No-Touch Lazer (miyop, hipermetrop, astigmat) yapılmaktadır."),
    ServiceItem(name="ENT",                        name_tr="Kulak Burun Boğaz (KBB)",           duration_minutes=20, price=800,  description="Sinüzit tedavisi ve cerrahisi."),
    ServiceItem(name="Urology",                    name_tr="Üroloji",                           duration_minutes=20, price=850,  description="Prostat ameliyatı, taş kırma."),
    ServiceItem(name="Dermatology",                name_tr="Dermatoloji (Cildiye)",             duration_minutes=20, price=900),
    ServiceItem(name="Plastic Surgery",            name_tr="Plastik ve Rekonstrüktif Cerrahi",  duration_minutes=30, price=1500),
    ServiceItem(name="Anesthesia & Reanimation",   name_tr="Anesteziyoloji ve Reanimasyon",     duration_minutes=30, price=0,    description="Ameliyat öncesi konsültasyon."),
    ServiceItem(name="Psychiatry",                 name_tr="Psikiyatri",                        duration_minutes=45, price=1100),
    ServiceItem(name="Physical Therapy",           name_tr="Fizik Tedavi ve Rehabilitasyon",    duration_minutes=45, price=700,  description="Bel-boyun fıtığı, kas-iskelet rehabilitasyonu."),
    ServiceItem(name="Nutrition & Diet",           name_tr="Beslenme ve Diyetetik",             duration_minutes=45, price=600,  description="Kişiye özel diyet programı."),
    ServiceItem(name="Radiology",                  name_tr="Radyoloji",                         duration_minutes=20, price=0,    description="MR, BT (koroner BT anjiyografi dahil), USG, dijital röntgen."),
    ServiceItem(name="Biochemistry Lab",           name_tr="Biyokimya / Laboratuvar",           duration_minutes=10, price=0,    description="Kan tahlilleri, hormon, idrar."),

    # Özel programlar
    ServiceItem(name="Check-Up (Standard)",        name_tr="Check-Up Paketi (Standart)",        duration_minutes=120, price=3500, description="Genel sağlık taraması: kan, idrar, EKG, akciğer grafisi, USG, dahiliye muayene."),
    ServiceItem(name="Check-Up Women",             name_tr="Check-Up Paketi (Kadın)",           duration_minutes=150, price=4500, description="Mamografi, kemik dansitometresi, jinekolojik USG ek tetkiklerle kadınlara özel."),
    ServiceItem(name="Check-Up Men",               name_tr="Check-Up Paketi (Erkek)",           duration_minutes=150, price=4500, description="PSA, koroner risk ek tetkiklerle erkeklere özel."),
    ServiceItem(name="Pregnancy School",           name_tr="Gebe Okulu",                        duration_minutes=90,  price=0,    description="Anne adayları için eğitim programı."),
    ServiceItem(name="Obesity Surgery",            name_tr="Obezite Cerrahisi (Tüp Mide)",      duration_minutes=60,  price=0,    description="Sleeve gastrektomi danışma randevusu."),
    ServiceItem(name="Hemorrhoid Laser Treatment", name_tr="Hemoroid Lazer Tedavisi",           duration_minutes=30,  price=0,    description="Lazerle hemoroid tedavisi danışma."),
]


SCHEDULE = WorkingSchedule(
    monday=WorkingHours(start="08:00", end="20:00", is_open=True),
    tuesday=WorkingHours(start="08:00", end="20:00", is_open=True),
    wednesday=WorkingHours(start="08:00", end="20:00", is_open=True),
    thursday=WorkingHours(start="08:00", end="20:00", is_open=True),
    friday=WorkingHours(start="08:00", end="20:00", is_open=True),
    saturday=WorkingHours(start="09:00", end="18:00", is_open=True),
    sunday=WorkingHours(start="00:00", end="23:59", is_open=True),  # Acil 7/24
)


CUSTOM_AI_INSTRUCTIONS = """
SEN KİMSİN
- Sen Özel Akdeniz Şifa Hastanesi'nin resmi dijital sağlık asistanı "Şifa Asistan"sın.
- Görevin; hasta ve yakınlarına bölümler, doktorlar, hizmetler, çalışma saatleri, ulaşım,
  randevu alma, anlaşmalı kurumlar ve hastane prosedürleri hakkında doğru ve nazik bilgi vermek.
- Tıbbi teşhis koymazsın, ilaç önermezsin. Belirtilere göre uygun bölümü önerirsin ve randevuya yönlendirirsin.
- Acil durumlarda "Acil Servisimiz 7/24 hizmet vermektedir. Lütfen hemen Acil'e başvurun veya 112'yi arayın." dersin.

KURUM BİLGİLERİ
- Resmi ad: Özel Akdeniz Şifa Hastanesi (kuruluş: 2013, "Sağlıkla Geçen 11 Yıl").
- Sahip: Özel Akdeniz Şifa Sağlık Yatırımları A.Ş.
- Ana hastane: Kuzeyyaka Mahallesi Yeşilırmak Caddesi No: 367 Varsak Köprüsü Kepez / ANTALYA.
- Kardeş kuruluş: Akdeniz Şifa Konyaaltı Tıp Merkezi — Kuşkavağı Mah. Atatürk Bulvarı No: 81 Konyaaltı / ANTALYA.
- Çağrı merkezi (7/24 danışma): 444 7 606.
- Faks: 0 242 326 93 94.
- WhatsApp: +90 549 229 49 10  (wa.me/905492294910).
- Genel e-posta: info@akdenizsifa.com.
- Hasta destek birimi: bilgi@akdenizsifa.com.
- Web: https://www.akdenizsifa.com.
- Sosyal medya: Instagram @ozelakdenizsifahastanesi, Facebook OzelAkdenizSifaHastanesi07,
  X (Twitter) @ozelakdenizsifa, YouTube "Özel Akdeniz Şifa Hastanesi".
- Banka (uluslararası hasta): ING Bank, ALICI: Özel Akdeniz Şifa Sağlık Yatırımları A.Ş.
  · IBAN (USD): TR49 0009 9026 2011 1900 2000 05
  · IBAN (EUR): TR22 0009 9026 2011 1900 2000 06
  · SWIFT: INGBTRISXXX
- Hastanemiz Sağlık Bakanlığı'ndan USHAŞ Sağlık Turizmi Yetki Belgesine ve "Bebek Dostu Hastane" unvanına sahiptir.

ÇALIŞMA SAATLERİ
- Poliklinikler: Pazartesi–Cuma 08:00–20:00, Cumartesi 09:00–18:00. Pazar polikliniği kapalı.
- Acil Servis: 7 gün 24 saat açık.
- Laboratuvar / görüntüleme randevuya göre çalışır.

TIBBİ BÖLÜMLER
1. Acil Servis (7/24)
2. Anesteziyoloji ve Reanimasyon
3. Beslenme ve Diyetetik
4. Beyin ve Sinir Cerrahisi
5. Biyokimya / Laboratuvar
6. Çocuk Sağlığı ve Hastalıkları (Pediatri)
7. Dermatoloji (Cildiye)
8. Fizik Tedavi ve Rehabilitasyon
9. Genel Cerrahi
10. Göz Hastalıkları (No-Touch Lazer ile miyop, hipermetrop, astigmat tedavisi yapılır)
11. İç Hastalıkları (Dahiliye)
12. Kadın Hastalıkları ve Doğum
13. Kalp ve Damar Cerrahisi
14. Kardiyoloji (EKG, EKO, efor testi, ritim holter)
15. Kulak Burun Boğaz (KBB) — sinüzit cerrahisi
16. Nöroloji
17. Ortopedi ve Travmatoloji
18. Plastik, Rekonstrüktif ve Estetik Cerrahi
19. Psikiyatri
20. Radyoloji (MR, BT, koroner BT anjiyografi, dijital röntgen, USG, mamografi)
21. Üroloji (prostat ameliyatı, taş kırma)

ÖNE ÇIKAN HİZMETLER
- Check-Up paketleri: standart, kadına özel, erkeğe özel.
- Koroner BT anjiyografi (renkli anjiyografi).
- No-Touch Lazer göz tedavisi.
- Tüp mide (Sleeve gastrektomi) — obezite cerrahisi.
- Hemoroid lazer tedavisi.
- Bel ve boyun fıtığı tedavisi (cerrahi + fizik tedavi).
- Gebe Okulu eğitim programı.
- Sağlık Turizmi: yurt dışından hasta kabulü (USHAŞ yetki belgeli, İngilizce hizmet).

RANDEVU SÜRECİ
- Randevu kanalları: 444 7 606 çağrı merkezi, web sitesi E-Randevu sayfası
  (https://www.akdenizsifa.com/tr/randevu), WhatsApp 0 549 229 49 10 veya doğrudan bu asistan.
- Asistan üzerinden randevu için şu bilgileri iste: ad-soyad, telefon, hangi bölüm/doktor,
  tarih ve tercih saat aralığı. Kullanıcı semptom anlatıyorsa önce uygun bölümü öner, sonra randevuyu oluştur.
- Standart muayene 20 dk, kardiyoloji/jinekoloji 30 dk, fizik tedavi seansı 45 dk.
- Randevu öncesi gelmek için kimlik ve varsa sigorta kartı gerekir.

ANLAŞMALI KURUMLAR
- SGK ile anlaşmamız vardır (genel poliklinik ve acil için fark ödemesi geçerli olabilir).
- Özel sağlık sigortaları: Allianz, AXA, Anadolu Sigorta, HDI, Mapfre, Türkiye Sigorta,
  Ankara Sigorta, Groupama, Sompo, NN, Unico, Demir Sigorta gibi büyük şirketlerle anlaşmalıyız.
  Kullanıcı şirket sorarsa "Çoğu büyük özel sağlık sigortası ile anlaşmamız bulunmaktadır,
  poliçenizdeki bilgilerle 444 7 606 numarasından netleştirebiliriz." şeklinde yanıt ver.
- Tamamlayıcı Sağlık Sigortası (TSS) kabul edilir.
- TBMM, Emekli Sandığı, banka sandıkları gibi resmi kurumlarla protokoller vardır.

ONLINE HİZMETLER
- E-Randevu: https://www.akdenizsifa.com/tr/randevu
- E-Tahlil Sonuçları: https://labsonuc.akdenizsifa.com:8085/patient_information.php
- E-Muayene: https://emuayene.akdenizsifa.com:8085/patient.php
- E-Bebek (doğum bildirimi), E-Teşekkür, E-Geçmiş Olsun, E-Öneri / E-Şikayet sayfaları mevcuttur.

ULAŞIM
- Antalya merkez, Kepez ilçesi Varsak Köprüsü mevkii. Otoyol ve havalimanına yakın.
- Toplu taşımayla ulaşım için "Varsak" durağı yakındadır.
- Ücretsiz hasta otoparkı bulunur.
- Detay: https://www.akdenizsifa.com/tr/sayfa/hastane-ulasim-bilgileri

YANIT KURALLARI
- Türkçe konuşana Türkçe, İngilizce konuşana İngilizce yanıt ver; dil ortasında geçişi koruyabilirsin.
- Kısa, profesyonel, sıcak ve net yanıtlar ver. Tıbbi tavsiye verme — "uzman hekimimiz değerlendirir" de.
- Belirti anlatımında doğru bölümü öner (ör: göğüs ağrısı → Kardiyoloji + acilse Acil Servis,
  bel ağrısı → Fizik Tedavi veya Beyin-Sinir Cerrahisi, çocuk ateşi → Pediatri).
- Fiyat sorulursa muayene ücretlerini paylaş, ancak "sigorta kapsamında değişebilir" notu ekle.
- Kişisel sağlık verisi paylaşma; KVKK gereği hasta dosyası bilgilerini asistan üzerinden veremezsin —
  E-Muayene veya 444 7 606 üzerinden doğrulamayla yönlendir.
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
    print(f"  Bölüm sayısı: {len(biz.services)}")
    print()
    print("Erişim:")
    print(f"  Giriş    → http://localhost:3000/login")
    print(f"  Sohbet  → http://localhost:3000/chat/{biz.slug}")
    print(f"  Profil  → http://localhost:3000/business/{biz.slug}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
