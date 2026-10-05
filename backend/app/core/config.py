from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration. Every field must also appear in .env.example.

    Defaults target a host-run backend (`make ... LOCAL=1`) talking to the compose db on
    localhost:5432; inside compose, .env overrides the URLs with the `db` host.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "postgresql+psycopg://blog:blog@localhost:5432/blog"
    test_database_url: str = "postgresql+psycopg://blog:blog@localhost:5432/blog_test"

    jwt_secret: SecretStr = SecretStr("local-dev-only-secret-change-me-0123456789")
    jwt_expire_minutes: int = 1440
    cookie_secure: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
