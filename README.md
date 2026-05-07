# AssistantAI – Yapay Zeka Destekli Randevu Sistemi

GPT-4o destekli, Google Takvim entegreli akıllı randevu platformu. Dövme stüdyoları, klinikler, güzellik merkezleri ve daha fazlası için.

## Özellikler

- 🤖 **GPT-4o AI Chatbot** – Müşterileri Türkçe/İngilizce karşılar, ihtiyaçlarını anlar
- 📅 **Google Takvim Entegrasyonu** – Randevular otomatik takvime eklenir, çakışma olmaz
- 🏢 **Çoklu Sektör** – Dövme, klinik, güzellik merkezi, kuaför ve daha fazlası
- 🔗 **Paylaşılabilir Chat Linki** – Her işletmeye özel müşteri chat sayfası
- 📊 **Dashboard** – Tüm randevuları tek ekrandan yönet, iptal et

## Teknoloji Stack

| Katman     | Teknoloji                        |
| ---------- | -------------------------------- |
| Backend    | Python 3.12, FastAPI, Beanie ODM |
| AI         | OpenAI GPT-4o (function calling) |
| Veritabanı | MongoDB                          |
| Takvim     | Google Calendar API v3           |
| Frontend   | Next.js 15, React 19, TypeScript |
| UI         | Tailwind CSS                     |
| Auth       | JWT (python-jose)                |

## Hızlı Başlangıç

### Gereksinimler

- Python 3.12+
- Node.js 20+
- MongoDB (veya Docker)
- OpenAI API Key
- Google Cloud Console projesi (Calendar API etkin)

### Backend

```bash
cd backend

# Ortam dosyasını oluştur
cp .env.example .env
# .env dosyasını düzenle (OPENAI_API_KEY, GOOGLE_* vb.)

# Sanal ortam oluştur ve bağımlılıkları yükle
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Başlat
uvicorn app.main:app --reload
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

cp .env.example .env.local
npm install
npm run dev
# http://localhost:3000
```

### Docker ile (tümü bir arada)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# .env dosyalarını düzenle

docker-compose up --build
```

## Kullanım Akışı

1. **İşletme Kaydı** → `/register` – Sektörünüzü seçin, URL adınızı belirleyin
2. **Google Takvim Bağlantısı** → Dashboard → Ayarlar → "Google ile Bağlan"
3. **Chat Linkini Paylaşın** → `/chat/{slug}` adresini müşterilerinize gönderin
4. **AI Otomatik Halleder** → Müşteri sohbet eder, uygun saati seçer, randevu oluşur

## Google Calendar Kurulumu

1. [Google Cloud Console](https://console.cloud.google.com)'a gidin
2. Yeni proje oluşturun
3. **Google Calendar API**'yi etkinleştirin
4. **OAuth 2.0 Client ID** oluşturun (Web application)
5. Authorized redirect URI ekleyin: `http://localhost:8000/api/calendar/oauth/callback`
6. `client_id` ve `client_secret`'ı `.env` dosyasına ekleyin

## Proje Yapısı

```
AssistantAI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Ayarlar
│   │   ├── core/                # Auth, DB, Security
│   │   ├── models/              # MongoDB döküman modelleri
│   │   ├── routers/             # API endpoint'leri
│   │   └── services/            # AI, Calendar, Appointment servisleri
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── page.tsx             # Ana sayfa
    │   ├── login/ register/     # Auth sayfaları
    │   ├── dashboard/           # Yönetim paneli
    │   └── chat/[businessSlug]/ # Müşteri chat sayfası
    ├── components/
    │   └── chat/                # ChatWidget, MessageBubble
    └── lib/api.ts               # API istemcisi
```

## Lisans

MIT
