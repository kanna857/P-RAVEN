import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAVEN VOICE AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "raven-intelligence-platform-secret-key-super-secure-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Gnani AI Configuration
    # Official Base URL: https://api.vachana.ai
    # Authentication Header: X-API-Key-ID: <GNANI_API_KEY>
    GNANI_API_KEY: Optional[str] = os.getenv("GNANI_API_KEY", "")
    GNANI_BASE_URL: str = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai")
    GNANI_PRISMA_MODEL: str = os.getenv("GNANI_PRISMA_MODEL", "prisma-v3.0")
    GNANI_TIMBRE_MODEL: str = os.getenv("GNANI_TIMBRE_MODEL", "timbre-v2.5")
    
    # Optional Gnani Evon 30B / Reasoning Endpoint (OpenAI-compatible vLLM/SGLang or Enterprise)
    EVON_BASE_URL: Optional[str] = os.getenv("EVON_BASE_URL", "")
    EVON_API_KEY: Optional[str] = os.getenv("EVON_API_KEY", "")
    EVON_MODEL_NAME: str = os.getenv("EVON_MODEL_NAME", "gnani/gnani-evon-v3.3-30B-A3B")

    # Storage
    STORAGE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./raven.db")

    # Features
    DEMO_MODE_ALLOWED: bool = True
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
