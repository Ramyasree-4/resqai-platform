"""
ResQAI – Application Settings
Loads .env from the project root using absolute path — works regardless of CWD.
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env to an absolute path — always works regardless of CWD
_ROOT = Path(__file__).resolve().parent.parent.parent   # backend/
_ENV_FILE = _ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "ResQAI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000

    # ── Firebase ─────────────────────────────────────────────────────────
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = None
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    FIREBASE_PROJECT_ID: str = "resqai-dev"
    FIREBASE_STORAGE_BUCKET: str = "resqai-dev.appspot.com"
    FIREBASE_WEB_API_KEY: str = "placeholder"

    # ── Mistral AI (Primary LLM) ─────────────────────────────────────────
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-large-latest"
    MISTRAL_TIMEOUT_SECONDS: int = 30
    MISTRAL_MAX_RETRIES: int = 3

    # ── Google Gemini (Fallback LLM) ─────────────────────────────────────
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_PRIMARY_MODEL: str = "gemini-1.5-pro"
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"
    GEMINI_TIMEOUT_SECONDS: int = 30
    GEMINI_MAX_RETRIES: int = 3

    @property
    def resolved_gemini_key(self) -> Optional[str]:
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY

    # ── LangSmith ────────────────────────────────────────────────────────
    LANGSMITH_API_KEY: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "ResQAI"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    @property
    def langsmith_enabled(self) -> bool:
        return bool(self.LANGSMITH_API_KEY or self.LANGCHAIN_API_KEY) and self.LANGCHAIN_TRACING_V2

    # ── JWT ──────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "resqai-default-dev-secret-key-please-change!!"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ── Rate Limiting ────────────────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_AI: str = "20/minute"

    # ── Google Maps ──────────────────────────────────────────────────────
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # ── Notifications ────────────────────────────────────────────────────
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "alerts@resqai.in"
    MSG91_API_KEY: Optional[str] = None
    MSG91_SENDER_ID: str = "RESQAI"

    # ── Cloud Storage ────────────────────────────────────────────────────
    GCS_MEDIA_BUCKET: str = "resqai-media"
    GCS_EXPORTS_BUCKET: str = "resqai-exports"
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── Logging ──────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"

    # ── AI Circuit Breaker ───────────────────────────────────────────────
    AI_CIRCUIT_BREAKER_THRESHOLD: int = 5
    AI_CIRCUIT_BREAKER_TIMEOUT: int = 60

    # ── SLA (minutes) ────────────────────────────────────────────────────
    SLA_CRITICAL_MINUTES: int = 30
    SLA_HIGH_MINUTES: int = 60
    SLA_MEDIUM_MINUTES: int = 120
    SLA_LOW_MINUTES: int = 240

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def firebase_web_api_key(self) -> str:
        """Always read from os.getenv first to bypass any caching."""
        return os.getenv("FIREBASE_WEB_API_KEY") or self.FIREBASE_WEB_API_KEY


# ── Single module-level instance — created once at import ───────────────────
# We do NOT use lru_cache. Instead we create one instance here.
# Every module imports `settings` directly from this module.
settings = Settings()


def get_settings() -> Settings:
    """Return the module-level Settings instance."""
    return settings
