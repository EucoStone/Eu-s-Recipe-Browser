from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "RecipeBrowser"
    app_env: str = "development"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "recipe_browser"
    upload_dir: str = "uploads"
    cors_origins: str = "http://localhost:5173"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_origins(cls, value: str | List[str]) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
