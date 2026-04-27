"""Celery application and beat schedule configuration."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "dental_bot_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={"app.workers.tasks.*": {"queue": "default"}},
    beat_schedule={
        "send-appointment-reminders-hourly": {
            "task": "app.workers.tasks.send_appointment_reminders",
            "schedule": crontab(minute=0),
        },
        "process-no-shows-daily": {
            "task": "app.workers.tasks.process_no_shows",
            "schedule": crontab(minute=0, hour=10),
        },
        "cleanup-expired-locks-every-5m": {
            "task": "app.workers.tasks.cleanup_expired_locks",
            "schedule": crontab(minute="*/5"),
        },
    },
)

__all__ = ["celery_app"]
