"""Application configuration loaded from environment variables via python-dotenv."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the service root (parent of app/)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


class Settings:
    """Runtime settings for the user microservice."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "User Service")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

        # Database URL must come from an environment variable
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is required. "
                "Copy .env.example to .env and set DATABASE_URL."
            )
        self.database_url: str = database_url

        cors_origins = os.getenv("CORS_ORIGINS", "*").strip()
        if cors_origins == "*":
            self.cors_origins: list[str] = ["*"]
        else:
            self.cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
