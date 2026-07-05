"""Configuration check / integration status route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict

from app.api.v1.routes.deps import get_current_staff_user
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.models.staff_user import StaffUser
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/config-check", tags=["config-check"])


class IntegrationStatus(BaseModel):
    service: str
    status: str
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [{"service": "Database", "status": "CONFIGURED"}, {"service": "Redis", "status": "MISSING"}]})


@router.get("/status", summary="Check integration configuration status", description="Returns the configuration status of all third-party integrations such as Database, Redis, Twilio, Stripe, and others. Each integration is reported as CONFIGURED, MISSING, or ENABLED.", response_description="List of integration statuses")
@limiter.limit("10/minute")
async def get_config_status(
    request: Request,
    _: StaffUser = Depends(get_current_staff_user),
) -> ResponseEnvelope[list[IntegrationStatus]]:
    settings = get_settings()

    checks = [
        IntegrationStatus(service="Database", status="CONFIGURED" if settings.database_url else "MISSING"),
        IntegrationStatus(service="Redis", status="CONFIGURED" if settings.redis_url else "MISSING"),
        IntegrationStatus(service="Anthropic (Claude)", status="CONFIGURED" if settings.anthropic_api_key else "MISSING"),
        IntegrationStatus(service="Deepgram", status="CONFIGURED" if settings.deepgram_api_key else "MISSING"),
        IntegrationStatus(service="Pinecone", status="CONFIGURED" if settings.pinecone_api_key else "MISSING"),
        IntegrationStatus(
            service="Twilio SMS",
            status="CONFIGURED" if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_phone_number else "MISSING",
        ),
        IntegrationStatus(
            service="Twilio WhatsApp",
            status="CONFIGURED" if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_whatsapp_from else "MISSING",
        ),
        IntegrationStatus(
            service="SendGrid Email",
            status="CONFIGURED" if settings.sendgrid_api_key and settings.sendgrid_from_email else "MISSING",
        ),
        IntegrationStatus(
            service="Stripe Payments",
            status="CONFIGURED" if settings.stripe_secret_key and settings.stripe_webhook_secret else "MISSING",
        ),
        IntegrationStatus(
            service="Google Calendar",
            status="CONFIGURED" if settings.google_client_id and settings.google_client_secret and settings.google_redirect_uri else "MISSING",
        ),
        IntegrationStatus(
            service="S3 Backup",
            status="CONFIGURED" if settings.backup_s3_bucket and settings.backup_aws_access_key_id and settings.backup_aws_secret_access_key else "MISSING",
        ),
        IntegrationStatus(service="Sentry", status="CONFIGURED" if settings.sentry_dsn else "MISSING"),
        IntegrationStatus(service="Prometheus", status="ENABLED" if settings.prometheus_enabled else "DISABLED"),
    ]

    return ResponseEnvelope.success_response(data=checks)


__all__ = ["router"]
