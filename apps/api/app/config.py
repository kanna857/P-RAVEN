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
    
    # Ollama Local Reasoning Model Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_TIMEOUT_SECONDS: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

    # Optional Gnani Evon 30B / Reasoning Endpoint (OpenAI-compatible vLLM/SGLang or Enterprise)
    EVON_BASE_URL: Optional[str] = os.getenv("EVON_BASE_URL", "")
    EVON_API_KEY: Optional[str] = os.getenv("EVON_API_KEY", "")
    EVON_MODEL_NAME: str = os.getenv("EVON_MODEL_NAME", "gnani/gnani-evon-v3.3-30B-A3B")

    # Nhost BaaS Configuration (PostgreSQL + S3 Storage + Hasura GraphQL)
    NHOST_SUBDOMAIN: Optional[str] = os.getenv("NHOST_SUBDOMAIN", "")
    NHOST_REGION: Optional[str] = os.getenv("NHOST_REGION", "")
    NHOST_ADMIN_SECRET: Optional[str] = os.getenv("NHOST_ADMIN_SECRET", "")

    # Storage & Database
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
os.makedirs(os.path.join(settings.STORAGE_DIR, "preprocessed"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "briefings"), exist_ok=True)
