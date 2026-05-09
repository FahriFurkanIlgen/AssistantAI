from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# .env her zaman backend/ klasöründen okunur, CWD'den bağımsız
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AssistantAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-strong-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "assistantai"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Google Calendar
    GOOGLE_CLIENT_ID: str = "814011281114-m21cidd7s4ncbg6aienvhqqcabqp0di4.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/calendar/oauth/callback"

    # SMTP Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""       # Gmail: App Password (16 chars, no spaces)
    SMTP_FROM: str = ""           # e.g. yourapp@gmail.com

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = True


settings = Settings()
