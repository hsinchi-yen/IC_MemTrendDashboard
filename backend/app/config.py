"""
backend/app/config.py
Application configuration using pydantic-settings.
All secrets are loaded from environment variables / .env file.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for IC_MemTrendDashboard backend.

    Values are read from environment variables first, then from a
    ``.env`` file in the project root (relative to the process CWD).
    """

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str

    # ------------------------------------------------------------------ #
    # External data APIs
    # ------------------------------------------------------------------ #
    FINMIND_TOKEN: str = ""
    ALPHA_VANTAGE_KEY: str = ""

    # ------------------------------------------------------------------ #
    # Notification channels
    # ------------------------------------------------------------------ #
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    LINE_NOTIFY_TOKEN: str = ""

    # ------------------------------------------------------------------ #
    # SMTP / e-mail
    # ------------------------------------------------------------------ #
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    ALERT_EMAIL_TO: str = ""

    # ------------------------------------------------------------------ #
    # LLM
    # ------------------------------------------------------------------ #
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"  # gemini | openai | anthropic

    # ------------------------------------------------------------------ #
    # Data-freshness thresholds (hours)
    # ------------------------------------------------------------------ #
    DATA_FRESHNESS_THRESHOLD_HOURS_STOCK: int = 12
    DATA_FRESHNESS_THRESHOLD_HOURS_QUOTE: int = 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of :class:`Settings`.

    Using ``lru_cache`` ensures the ``.env`` file is parsed only once per
    process lifetime, which is the recommended pattern for pydantic-settings.

    Returns
    -------
    Settings
        The application settings instance.
    """
    return Settings()
