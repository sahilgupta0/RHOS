"""
RHOS Application Configuration.

Centralized configuration loaded from environment variables via Pydantic Settings.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "RHOS"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # --- Authentication ---
    auth_mode: Literal["firebase", "local"] = "local"
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # --- Firebase ---
    firebase_credentials: str = "./firebase-service-account.json"
    firebase_storage_bucket: str = ""

    # --- MongoDB ---
    mongodb_uri: str = ""
    mongodb_db_name: str = "rhos"

    # --- Google Gemini AI ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # --- Google Cloud Speech (optional) ---
    google_speech_enabled: bool = False

    # --- Google Cloud TTS (optional) ---
    google_tts_enabled: bool = False

    # --- Google Maps (optional) ---
    google_maps_api_key: str = ""

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 60

    # --- Datasets ---
    datasets_path: str = "../datasets"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_firebase_configured(self) -> bool:
        """Check if Firebase credentials are configured."""
        return bool(self.firebase_credentials and self.firebase_storage_bucket)

    @property
    def is_mongodb_configured(self) -> bool:
        """Check if MongoDB URI is configured."""
        return bool(self.mongodb_uri)

    @property
    def is_gemini_configured(self) -> bool:
        """Check if Gemini API is configured."""
        return bool(self.gemini_api_key)


# Singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
