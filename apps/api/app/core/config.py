from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = "Autonomous Dental Appointment Bot"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    secret_key: str = Field(default="change-me")
    access_token_expire_minutes: int = Field(default=60)

    database_url: str = Field(default="sqlite+aiosqlite:///./dev.db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")
    frontend_base_url: str = Field(default="http://localhost:3000")

    anthropic_api_key: str | None = Field(default=None)
    deepgram_api_key: str | None = Field(default=None)
    pinecone_api_key: str | None = Field(default=None)
    pinecone_environment: str | None = Field(default=None)

    twilio_account_sid: str | None = Field(default=None)
    twilio_auth_token: str | None = Field(default=None)
    twilio_phone_number: str | None = Field(default=None)

    sendgrid_api_key: str | None = Field(default=None)
    sendgrid_from_email: str | None = Field(default=None)

    stripe_secret_key: str | None = Field(default=None)
    stripe_webhook_secret: str | None = Field(default=None)

    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)
    google_redirect_uri: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
