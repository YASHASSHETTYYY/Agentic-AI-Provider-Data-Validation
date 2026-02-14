from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Provider Operations Platform"
    environment: str = "dev"
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 120

    database_url: str = "sqlite:///./provider_ops.db"
    cors_origins: list[str] = ["http://localhost:5173"]

    bootstrap_admin_email: str = "admin@providerops.local"
    bootstrap_admin_password: str = "ChangeMe123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            if value.startswith("["):
                parsed = json.loads(value)
                return [str(item).strip() for item in parsed if str(item).strip()]
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise ValueError("Invalid CORS origins format.")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
