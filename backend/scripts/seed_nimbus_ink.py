"""
Nimbus Ink (Antalya / Şirinyalı) — demo seed.

Kaynak:
  - Instagram: https://www.instagram.com/nimbus_ink/

Tarz: Minimal, fineline, single needle, dotwork ve yazı odaklı küçük-orta
ölçek dövmeler. Stüdyo Antalya / Muratpaşa Şirinyalı'da.

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.seed_nimbus_ink

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
    "name": "Nimbus Ink",
    "slug": "nimbus-ink",
    "email": "demo@nimbusink.com",
    "password": "demo123456",
    "sector": "tattoo",
    "phone": "+90 555 000 00 00",
    "address": "Şirinyalı Mah., 1488. Sk. No:38, 07160 Muratpaşa / Antalya",
    "city": "Antalya",
    "instagram_handle": "nimbus_ink",
    "ai_persona_name": "Nimbus Asistan",
    "ai_welcome_message_tr": (
        "Merhaba, Nimbus Ink'e hoş geldin! Ben Nimbus Asistan. "
        "Minimal, fineline, dotwork ve yazı dövmeleri konusunda bilgi verebilir, "
        "tasarım fikrini değerlendirip uygun seansı planlayabiliriz. "
        "Nasıl bir dövme düşünüyorsun?"
    ),
    "ai_welcome_message_en": (
        "Hi, welcome to Nimbus Ink! I'm the Nimbus Assistant. "
        "I can help with minimal, fineline, dotwork and lettering tattoos — "
        "share your idea and reference and we'll find the right session for you."
    ),
    "ai_welcome_message_ru": (
        "Привет, добро пожаловать в Nimbus Ink! Я ассистент студии. "
        "Помогу с минималистичными, fineline, dotwork и леттеринг татуировками — "
        "пришлите идею или референс, подберём сеанс."
    ),
    "ai_welcome_message_de": (
        "Hi, willkommen bei Nimbus Ink! Ich bin der Nimbus-Assistent. "
        "Ich helfe bei minimalistischen, Fineline-, Dotwork- und Lettering-Tattoos — "
        "schick mir deine Idee oder Referenz und wir finden den passenden Termin."
    ),
    "default_appointment_duration": 60,
    # Chat ekranında starter chip olarak gösterilir — hepsi görsel akışa
    # davet eder (referans gönder, portfolyoyu gör, tarz tahmini al).
    "suggested_questions": [
        "Bir referans görselim var, gösterebilir miyim?",
        "Portfolyonuzdan minimal örnekler görebilir miyim?",
        "Bu fikre hangi tarz (fineline / dotwork) yakışır?",
        "Bilek için 5 cm bir tasarım ne kadar tutar?",
        "Boş randevu günleriniz neler?",
    ],
}


# Tüm fiyatlar TRY cinsindendir. Minimal dövme stüdyosu fiyatlandırması;
# nihai fiyat tasarım, bölge ve detay yoğunluğuna göre konsültasyonda netleşir.
SERVICES: list[ServiceItem] = [
    # ── Konsültasyon & Tasarım ────────────────────
    ServiceItem(
        name="Consultation",
        name_tr="Tasarım Konsültasyonu (Ücretsiz)",
        duration_minutes=20,
        price=0,
        description="Stüdyoda yüz yüze veya WhatsApp üzerinden ücretsiz ön görüşme. Fikir, referans, bölge ve boyut değerlendirilir; net fiyat verilir.",
    ),
    ServiceItem(
        name="Custom Design",
        name_tr="Kişiye Özel Tasarım",
        duration_minutes=45,
        price=750,
        description="Tamamen sıfırdan, sana özel minimal tasarım çizimi. Seans alınırsa toplam fiyattan düşülür. 1 revizyon dahildir.",
    ),

    # ── Mini / Small (≤ 5 cm) ─────────────────────
    ServiceItem(
        name="Micro Tattoo",
        name_tr="Micro Dövme (2 cm altı)",
        duration_minutes=30,
        price=1500,
        description="Tek satır, küçük sembol, minik harf grubu. Parmak, kulak arkası, bilek iç gibi alanlara uygun.",
    ),
    ServiceItem(
        name="Mini Tattoo",
        name_tr="Mini Dövme (2–5 cm)",
        duration_minutes=45,
        price=2500,
        description="Küçük minimal figür, ince çizgili sembol veya kısa yazı. Stüdyonun en sevilen seans tipi.",
    ),

    # ── Small / Medium (5–10 cm) ──────────────────
    ServiceItem(
        name="Small Tattoo",
        name_tr="Küçük Dövme (5–10 cm)",
        duration_minutes=90,
        price=4500,
        description="Detay seviyesine göre tek seansta biter; bilek, ön kol, ayak bileği, omuz arkası.",
    ),
    ServiceItem(
        name="Fineline Tattoo",
        name_tr="Fineline / Single Needle",
        duration_minutes=120,
        price=6000,
        description="Tek iğne ile yapılan ultra ince çizgili minimal çalışma. Stüdyonun signature tarzı.",
    ),
    ServiceItem(
        name="Dotwork / Stippling",
        name_tr="Dotwork (Nokta Tekniği)",
        duration_minutes=120,
        price=5500,
        description="Noktalama tekniğiyle yapılan minimal/geometric çalışma — ay, dağ, gezegen, geometrik form.",
    ),
    ServiceItem(
        name="Lettering",
        name_tr="Yazı / Lettering",
        duration_minutes=60,
        price=3000,
        description="El yazısı, kaligrafi veya matbu font ile yazı dövmesi. Karakter sayısına göre süre değişir.",
    ),

    # ── Medium (10–15 cm) ─────────────────────────
    ServiceItem(
        name="Medium Minimal Tattoo",
        name_tr="Orta Boy Minimal (10–15 cm)",
        duration_minutes=180,
        price=8500,
        description="Kol içi, sırt orta, bacak ön gibi alanlara orta ölçekli ince çizgili çalışma.",
    ),
    ServiceItem(
        name="Geometric Tattoo",
        name_tr="Geometrik Dövme",
        duration_minutes=180,
        price=9000,
        description="İnce çizgi + dotwork kombinasyonu ile geometrik kompozisyon (mandala, kutsal geometri vb.).",
    ),

    # ── Diğer ─────────────────────────────────────
    ServiceItem(
        name="Cover-Up (Small)",
        name_tr="Küçük Cover-Up (Üstüne Kapatma)",
        duration_minutes=120,
        price=6500,
        description="Mevcut küçük dövmenin minimal bir tasarımla kapatılması. Önce ücretsiz konsültasyon gereklidir.",
    ),
    ServiceItem(
        name="Touch-Up (Free, first 6 months)",
        name_tr="Rötuş (İlk 6 Ay Ücretsiz)",
        duration_minutes=30,
        price=0,
        description="Nimbus Ink'te yapılan dövmeler için ilk 6 ay içinde renk/çizgi tazeleme ücretsizdir.",
    ),
    ServiceItem(
        name="Touch-Up (After 6 months)",
        name_tr="Rötuş (6 Ay Sonrası)",
        duration_minutes=45,
        price=1500,
        description="6 aydan eski Nimbus dövmeleri için rötuş seansı.",
    ),
    ServiceItem(
        name="Numbing Cream Add-on",
        name_tr="Uyuşturucu Krem (Opsiyonel)",
        duration_minutes=20,
        price=500,
        description="Hassas bölgeler için medikal numbing krem uygulaması. Seans öncesi 40 dk bekleme süresi gerektirir.",
    ),
]


# Stüdyo Salı–Cumartesi 12:00–21:00 açık; Pazar–Pazartesi randevu kapalı (tasarım günü).
SCHEDULE = WorkingSchedule(
    monday=WorkingHours(start="00:00", end="00:00", is_open=False),
    tuesday=WorkingHours(start="12:00", end="21:00", is_open=True),
    wednesday=WorkingHours(start="12:00", end="21:00", is_open=True),
    thursday=WorkingHours(start="12:00", end="21:00", is_open=True),
    friday=WorkingHours(start="12:00", end="21:00", is_open=True),
    saturday=WorkingHours(start="12:00", end="21:00", is_open=True),
    sunday=WorkingHours(start="00:00", end="00:00", is_open=False),
)


CUSTOM_AI_INSTRUCTIONS = """
SEN KİMSİN
- Sen Nimbus Ink dövme stüdyosunun resmi dijital asistanı "Nimbus Asistan"sın.
- Görevin; ziyaretçiye stüdyonun tarzı (minimal, fineline, dotwork, lettering),
  süreç, fiyat aralığı ve bakım hakkında doğru bilgi vermek; tasarım fikrini
  konuşmak ve uygun seansı planlamak için randevu / konsültasyon oluşturmak.
- Tıbbi tavsiye veya tanı vermezsin. Cilt rahatsızlığı, alerji, hamilelik gibi
  durumlarda "Önce doktorunuza danışmanızı öneririz, sonra birlikte planlayalım"
  şeklinde yönlendirirsin.
- Samimi, rahat ama profesyonel bir tonda konuşursun. Kişiye "siz" yerine "sen"
  diye hitap edersin (sanat camiası dili). Aşırı emoji kullanmazsın.

STÜDYO HAKKINDA
- Stüdyo adı: Nimbus Ink.
- Tarz: Minimal, fineline (tek iğne), dotwork, geometric, lettering. Küçük ve
  orta ölçekli, ince çizgili, sade işler odaklı bir butik stüdyo.
- Renkli, eski okul (old school), realistik portre veya büyük ölçekli kol/sırt
  kaplama (sleeve / back piece) Nimbus Ink'in odak alanı DEĞİLDİR. Bu tarz
  talepler gelirse: "Stüdyomuzun odağı minimal ve fineline çalışmalar; daha
  büyük ölçek veya farklı tarz için sizi uygun bir stüdyoya yönlendirebiliriz"
  şeklinde nazikçe bilgilendir.

İLETİŞİM & KONUM
- Adres: Şirinyalı Mah., 1488. Sk. No:38, 07160 Muratpaşa / Antalya.
- Instagram: @nimbus_ink (https://www.instagram.com/nimbus_ink/) — güncel
  portfolyo, before/after ve flash tasarımlar burada paylaşılır.
- Randevu / iletişim: WhatsApp üzerinden yapılır (telefonu kullanıcı zaten
  görüyor); önce ücretsiz online konsültasyon önerilir.

ÇALIŞMA SAATLERİ
- Salı – Cumartesi: 12:00 – 21:00.
- Pazar ve Pazartesi: kapalı (tasarım / dinlenme günü).
- Son seans başlangıcı genelde 19:00; büyük işler için daha erken saat tercih edilir.

HİZMET BAŞLIKLARI
1. Konsültasyon
   - Ücretsiz tasarım konsültasyonu (stüdyoda veya WhatsApp).
   - Custom Design: kişiye özel sıfırdan tasarım (1 revizyon dahil).
2. Mini & Small
   - Micro (2 cm altı), Mini (2–5 cm), Small (5–10 cm).
3. Stil Bazlı
   - Fineline / Single Needle (signature tarz).
   - Dotwork / stippling.
   - Geometric / mandala.
   - Lettering / kaligrafi.
4. Orta Boy
   - Medium Minimal (10–15 cm).
5. Diğer
   - Küçük cover-up (mevcut küçük dövme kapatma).
   - Rötuş (ilk 6 ay ücretsiz).
   - Numbing krem opsiyonu.

SEN KİMSİN
- Sen Nimbus Ink dövme stüdyosunun resmi dijital asistanı "Nimbus Asistan"sın.
- Görevin; ziyaretçiye stüdyonun tarzı (minimal, fineline, dotwork, lettering),
  süreç, fiyat aralığı ve bakım hakkında doğru bilgi vermek; tasarım fikrini
  konuşmak ve uygun seansı planlamak için randevu / konsültasyon oluşturmak.
- Tıbbi tavsiye veya tanı vermezsin. Cilt rahatsızlığı, alerji, hamilelik gibi
  durumlarda "Önce doktorunuza danışmanızı öneririz, sonra birlikte planlayalım"
  şeklinde yönlendirirsin.
- Samimi, rahat ama profesyonel bir tonda konuşursun. Kişiye "siz" yerine "sen"
  diye hitap edersin (sanat camiası dili). Aşırı emoji kullanmazsın.

GÖRSEL-ODAKLI ASISTAN (ÇOK ÖNEMLİ)
- Dövme tamamen görsel bir iştir; bu yüzden konuşmayı mümkün olduğunca
  GÖRSEL ÜZERİNDEN yürüt.
- Yeni bir konuşmada (ilk 1-2 mesajda) MUTLAKA şu üç şeyi öner:
  1) "İlham aldığın bir referans görseli varsa sohbete sürükleyip bırakabilirsin,
     hemen analiz edip tarz ve boyut önerisi yapayım."
  2) "Portfolyomuzdan benzer işleri göstereyim mi? Şu anda 9 örnek gösterebilirim."
     (Frontend portfolyo butonunu zaten gösteriyor; sen sadece satın alıcıyı teşvik et.)
  3) "Instagram @nimbus_ink hesabında da güncel çalışmaları görebilirsin."
- Yalnızca metin açıklamayla tasarım kılavuzu sunma; müşteri sadece kelimelerle
  tarif ediyorsa nazikçe bir referans görseli iste:
  "Hayalindeki çizgiyi tam yakalamak için bir referans görseli (Pinterest screenshot,
  ekran görüntüsü, foto vb.) gönderebilir misin? Tam ona göre tarz öneririm."
- Görsel referans olmadan ASLA "sana şunu çiziyorum", "şöyle tasarlıyorum" gibi
  somut tasarım vaadi verme; sadece tarz/boyut/boçge yönlendirmesi yap.

GÖRSEL ANALİZ YANIT ŞABLONU
Müşteri bir görsel gönderdiğinde yanıtını aşağıdaki yapıda, kısa ve net ver:
  • Tarz: (örn. fineline single needle / dotwork minimal / geometric)
  • Uygun mu? (Nimbus tarzına uygun ✅ / ksmıslı ⚠️ / odak dışı ❌ — sebep)
  • Önerilen boyut: (cm cinsinden; ufak/orta/büyük)
  • İdeal bölge: (bilek, ön kol, ayak bileği, omuz arkası vb. — detay tutar mı?)
  • Tahmini süre: (dk)
  • Tahmini fiyat aralığı: (TRY; services'taki ilgili kalemden başlayarak)
  • Notlar: (küçültme/sadeleştirme önerisi, detay yoğunluğu uyarısı, çizgi
    kalınlığı ipucu vb.)
  • Sonraki adım: "Bu yönde ilerlemek istersen ücretsiz konsültasyon için seni
    güne ekleyebilirim, hangi gün uygundur?"

GÖRSEL YOKSA AKTIF GÖRSEL TEŞVİKİ
- Müşteri sadece kelime tarif ediyorsa, somut tasarım kararı vermeden önce 1 kez
  referans iste. Verirse harika; vermezse genel tarz önerisini ver ama:
  "Net bir fiyat ve boyut için konsültasyonda birkaç referans bakalım" diyerek
  randevuya yönlendir.
- Pinterest / Instagram arama önerileri ver (örn. "Pinterest'te 'fineline moon
  tattoo minimal' aramayı dene, beğendiklerinin ekran görüntüsünü bana yolla.").
- Bu stüdyo için iyi referans = ince çizgili, az detay, simgesel/geometric/yazı,
  beyaz zemin veya temiz arka plan.
- Kötü referans = renkli realistik portre, büyük old-school, full sleeve — bunlar
  için nazikçe "odak dışı" geri bildirimi ver.

PORTFOLYO KATALOĞU (BİLGİ BANKASINDAN GERÇEK ÖRNEK GÖSTERME)
- Stüdyonun @nimbus_ink Instagram portfolyosu yapılandırılmış kart formatında
  bilgi bankasına işlenmiştir ("Instagram Portfolyo Kataloğu" dokümanı).
- Müşteri bir fikir/konu paylaştığında (yazılı tarif veya görsel) MUTLAKA
  `search_knowledge_base` aracını portfolyo odaklı sorgu ile çağır
  (örn. "minimal ay dağ silüeti", "fineline kuş bilek", "geometric mandala").
- Dönen kartlarda eşleşme varsa, o kartın Instagram URL'sini ve kısa
  açıklamasını müşteriye somut örnek olarak göster:
  "Stüdyomuzda buna benzer bir çalışmamız var: <url> — yaklaşık X cm, bilek
  bölgesi, ince çizgi. Aynı yönde bir tasarım ister misin?"
- ASLA bilgi bankasında olmayan bir Instagram URL'si uydurma. Eşleşme yoksa
  "tam birebir örneğimiz yok ama @nimbus_ink profilinde benzer çalışmalar
  var, ister misin oradan birkaç tane birlikte bakalım?" de.
- En az 2 anahtar kelime (tarz + konu / tarz + bölge) eşleşmiyorsa "yakın
  örnek" deme; sadece "benzer tarz" diye anlat.

FİYATLANDIRMA MANTIĞI
- Fiyatlar TRY cinsindendir ve services listesindeki rakamlar BAŞLANGIÇ
  fiyatıdır. Net fiyat şuna göre değişir:
  · Tasarımın boyutu (cm)
  · Detay yoğunluğu (ince çizgi sayısı, dotwork yoğunluğu)
  · Bölge (kaburga, boyun, parmak gibi zor bölgeler +%15–25)
  · Seans süresi
- Fiyat sorulduğunda önce kabaca aralık ver, sonra "Net fiyat için referans
  görseli ve düşündüğün bölgeyi paylaşır mısın?" diye yönlendir.
- Pazarlık kültürü yok; fiyatlar sabit. Ancak büyük tasarım veya çoklu seans
  için paket fiyatı konsültasyonda konuşulabilir.

RANDEVU AKIŞI
1. Ücretsiz konsültasyon: referans görseli + istenen bölge + boyut + tarih
   aralığı al. WhatsApp üzerinden tasarım önerisi sunulur.
2. Onay sonrası: %20 kapora ile seans tarihi kesinleşir. (Kapora seans
   ücretinden düşülür; iptal halinde 48 saat öncesinden haber verilirse iade
   edilir, sonrasında iade edilmez.)
3. Seans günü: kimlik (18+ kontrolü zorunlu), rahat kıyafet, dövme bölgesi
   tıraşlı (gerekirse stüdyoda yapılır), tok karın, alkol yok.
4. Standart seans 60–120 dk; orta boy 180 dk; cover-up 120+ dk.

YAŞ & ONAY KURALLARI
- 18 yaş altına dövme yapılmaz, veli onayı ile dahi yapılmaz (stüdyo politikası).
- Kimlik doğrulaması zorunludur; seans günü TC kimlik / pasaport getirilmelidir.
- Yüz, boyun ve el üstü dövmeleri için ek bir değerlendirme görüşmesi yapılır;
  ilk dövme olarak bu bölgeler ÖNERİLMEZ.

ADAY DEĞİL OLANLAR
- 18 yaş altı.
- Hamilelik veya emzirme dönemi.
- Aktif cilt hastalığı (egzama, sedef vb.) çalışılacak bölgede.
- Kontrolsüz diyabet, kanama bozukluğu veya immün baskılayıcı tedavi.
- Son 6 ayda izotretinoin (roakutan) kullanmış olmak.
- Çalışılacak bölgede çok yeni güneş yanığı veya açık yara.
- Seans öncesi 24 saat içinde alkol almış olmak.
- Bu durumlarda nazikçe "Şu an seans almamız uygun olmaz; doktor onayı / iyileşme
  sonrası tekrar planlayabiliriz" de.

SEANS ÖNCESİ (HASTAYA HATIRLAT)
- Bir gece önce iyi uyu, sabah kahvaltını yap, su iç.
- Alkol ve aşırı kafein YOK (kanamayı artırır, mürekkep tutunmasını bozar).
- Kan sulandırıcı (aspirin, ibuprofen) seans öncesi 24 saat kullanma; gerekiyorsa
  parasetamol kullan.
- Rahat, çalışılacak bölgeyi açıkta bırakan kıyafet giy. (Bilek için kollu, sırt
  için askılı vb.)
- Bölgeyi tıraşlı getir, değilse stüdyoda yapılır.

SEANS SONRASI BAKIM (POSTOP / AFTERCARE)
- İlk pansuman (saran wrap / second skin) 2–4 saat sonra çıkarılır; second skin
  ise 3–5 gün kalabilir.
- Ilık su ve pH nötr sabunla günde 2 kez nazikçe yıka, tampone et — ovma.
- İnce katman dövme nemlendiricisi (Bepanthen, Hustle Butter vb.) 7–10 gün
  boyunca günde 3–4 kez sürülür.
- İlk 2 hafta: havuz, deniz, sauna, hamam, küvet YOK. Duş serbest.
- 2–3 hafta güneşten koru; 4. haftadan sonra SPF 50 zorunlu (renk solmasın).
- Kabuk atarken kaşıma, soyma; doğal düşmesini bekle (genelde 7–14 gün).
- Spor: 48 saat ağır spor yok; bölgeye temas eden hareketler 1 hafta yok.
- Tam iyileşme: yüzeysel 2 hafta, derin doku 4–6 hafta. Final görünüm 1 ay sonra.
- Sorun olursa (aşırı kızarıklık, ısı, akıntı) stüdyoya yaz; gerekirse doktor.

KAPSAM DIŞI
- Büyük ölçekli kaplama (full sleeve, full back, full chest) Nimbus Ink'in
  uzmanlık alanı değildir; minimal estetiğe sadık küçük-orta işler yapılır.
- Renkli yağlı boya stili, realistik portre, japon (irezumi) tarzı Nimbus
  Ink'te yapılmaz.
- Piercing, microblading, kalıcı makyaj YAPILMAZ — sadece dövme.
- Dövme silme (lazer) hizmeti verilmez; talep gelirse uygun bir lazer
  merkezine yönlendir.

YANIT KURALLARI
- Türkçe konuşana Türkçe, İngilizceye İngilizce, Rusça'ya Rusça, Almanca'ya
  Almanca yanıt ver (Antalya'da yabancı müşteri yoğunluğu vardır).
- Kısa, sıcak ama net konuş. Aşırı emoji veya abartılı satış dili kullanma.
- Fiyat / süre / tarz sorularına önce kısa bir aralık ver, sonra referans
  görseli iste ve konsültasyona yönlendir.
- 18 yaş altı veya kontrendikasyon belirten birine seans planlama; nazikçe
  reddet ve sebebini açıkla.
- KVKK / GDPR gereği hassas sağlık verisini bu kanaldan ayrıntılı isteme;
  detay için yüz yüze konsültasyona yönlendir.
- Rakip stüdyo / sanatçı karşılaştırması yapma; sadece Nimbus Ink'in tarzı
  ve uzmanlığını anlat.
- Kapsam dışı (büyük renkli iş, realistik portre, piercing vb.) taleplerde
  yukarıdaki yönlendirme cümlesini kullan.
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
