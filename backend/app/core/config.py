from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agently API"
    api_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://agently_user:agently_password@localhost:5432/agently"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str | None = None
    jwt_secret_key: str = Field(default="change-me-in-dev")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

