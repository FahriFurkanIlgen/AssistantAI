from pydantic_settings import BaseSettings, NoDecode
from pydantic import field_validator
from typing import List
from typing_extensions import Annotated
from pathlib import Path
import json

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
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/calendar/oauth/callback"

    # SMTP Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""       # Gmail: App Password (16 chars, no spaces)
    SMTP_FROM: str = ""           # e.g. yourapp@gmail.com

    # CORS - JSON array veya virgulle ayrilmis string olarak verilebilir.
    # Ornek: ALLOWED_ORIGINS=https://foo.vercel.app,https://example.com
    # NoDecode -> pydantic-settings otomatik JSON parse etmesin, validator calissin
    ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = True


settings = Settings()
