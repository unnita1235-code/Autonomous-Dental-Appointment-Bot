from decimal import Decimal
from functools import lru_cache
from typing import Self

from pydantic import Field, field_validator, model_validator
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
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

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
    twilio_whatsapp_from: str | None = Field(default="whatsapp:+14155238886")
    twilio_whatsapp_list_picker_content_sid: str | None = Field(default=None)

    sendgrid_api_key: str | None = Field(default=None)
    sendgrid_from_email: str | None = Field(default=None)
    sendgrid_dynamic_template_id: str | None = Field(default=None)

    enforce_cancellation_policy: bool = Field(default=False)
    late_cancellation_refund_percent: Decimal = Field(default=Decimal("50"))
    anthropic_model: str = Field(default="claude-sonnet-4-20250514")

    stripe_secret_key: str | None = Field(default=None)
    stripe_webhook_secret: str | None = Field(default=None)

    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)
    google_redirect_uri: str | None = Field(default=None)
    google_calendar_refresh_token: str | None = Field(default=None)

    allowed_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60)
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    backup_retention_days: int = Field(default=30)
    backup_schedule: str = Field(default="0 2 * * *")
    backup_s3_bucket: str | None = Field(default=None)
    backup_aws_access_key_id: str | None = Field(default=None)
    backup_aws_secret_access_key: str | None = Field(default=None)
    backup_aws_region: str = Field(default="us-east-1")
    prometheus_enabled: bool = Field(default=False)
    sentry_dsn: str | None = Field(default=None)
    apm_enabled: bool = Field(default=False)
    s3_bucket: str | None = Field(default=None)
    s3_access_key_id: str | None = Field(default=None)
    s3_secret_access_key: str | None = Field(default=None)
    s3_region: str = Field(default="us-east-1")
    s3_endpoint_url: str | None = Field(default=None)


    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def production_safeguards(self) -> Self:
        if self.environment != "production":
            return self

        errors: list[str] = []

        # Core security
        if self.secret_key == "change-me":
            errors.append("secret_key must be changed from its default value")
        if "*" in self.cors_origins:
            errors.append("cors_origins must not contain the wildcard '*' in production")
        if self.debug:
            errors.append("debug must be False in production")
        if self.log_level in ("DEBUG", "INFO"):
            errors.append("log_level should be WARNING or ERROR in production")

        # Database
        if self.database_url.startswith("sqlite"):
            errors.append("database_url must not use SQLite in production")

        # AI — agent won't function without an Anthropic key
        if self.anthropic_api_key is None:
            errors.append("anthropic_api_key is required in production")

        # Redis / Celery — must point to real instances, not localhost
        if self.redis_url.startswith("redis://localhost"):
            errors.append("redis_url must not point to localhost in production")
        if self.celery_broker_url.startswith("redis://localhost"):
            errors.append("celery_broker_url must not point to localhost in production")
        if self.celery_result_backend.startswith("redis://localhost"):
            errors.append("celery_result_backend must not point to localhost in production")

        # Frontend
        if self.frontend_base_url.startswith("http://localhost"):
            errors.append("frontend_base_url must not point to localhost in production")

        # Allowed hosts
        if self.allowed_hosts == ["localhost", "127.0.0.1"]:
            errors.append("allowed_hosts must be explicitly configured for production")

        # Twilio — used for SMS and WhatsApp notifications
        if self.twilio_account_sid is None:
            errors.append("twilio_account_sid is required in production")
        if self.twilio_auth_token is None:
            errors.append("twilio_auth_token is required in production")
        if self.twilio_phone_number is None:
            errors.append("twilio_phone_number is required in production")

        # SendGrid — used for email notifications
        if self.sendgrid_api_key is None:
            errors.append("sendgrid_api_key is required in production")
        if self.sendgrid_from_email is None:
            errors.append("sendgrid_from_email is required in production")

        # Stripe — used for payment deposits
        if self.stripe_secret_key is None:
            errors.append("stripe_secret_key is required in production")
        if self.stripe_webhook_secret is None:
            errors.append("stripe_webhook_secret is required in production")

        if errors:
            raise ValueError(
                "Production configuration validation failed:\n  - "
                + "\n  - ".join(errors)
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
