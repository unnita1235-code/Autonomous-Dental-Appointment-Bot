import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    _HAS_SENTRY = True
except ImportError:
    _HAS_SENTRY = False
    sentry_sdk = None  # type: ignore[assignment]


def init_sentry() -> None:
    settings = get_settings()
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured; skipping initialization")
        return
    if not _HAS_SENTRY:
        logger.warning("sentry-sdk not installed; cannot initialize Sentry")
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        integrations=[
            FastApiIntegration(),
            CeleryIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=0.1 if settings.environment == "production" else 1.0,
        send_default_pii=False,
    )
    logger.info("Sentry initialized for environment=%s", settings.environment)


init_sentry()


__all__ = ["init_sentry"]
