"""Application configuration — loads settings from .env via pydantic-settings."""

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All runtime settings.  Values come from .env → environment variables → defaults."""

    gemini_api_key: SecretStr = Field(
        ...,
        description="Gemini API key (required)",
    )
    gemini_model: str = Field(
        default="gemini-3.8-flash",
        description="Gemini model name — swap to gemini-3.5-flash-lite for cheaper runs",
    )
    database_path: str = Field(
        default="invoices.db",
        description="Path to the local SQLite database file",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def load_settings() -> Settings:
    """Load and validate settings.  Fails fast with a helpful message."""
    try:
        return Settings()
    except Exception as e:
        raise SystemExit(
            f"❌ Configuration error: {e}\n"
            f"Make sure you have a .env file with GEMINI_API_KEY set.\n"
            f"See .env.example for the required format."
        ) from e
