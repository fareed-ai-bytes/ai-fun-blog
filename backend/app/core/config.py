from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration. Every field must also appear in .env.example."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
