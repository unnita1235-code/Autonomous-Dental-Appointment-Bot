import logging

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_prerun, worker_shutdown

from app.core.config import get_settings
from app.core.context import request_id_var, task_id_var

settings = get_settings()

logger = logging.getLogger(__name__)

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


@task_prerun.connect
def propagate_context(task_id, task, args, kwargs, **kw):
    rid = kwargs.get("__request_id__", "")
    if rid:
        request_id_var.set(rid)
    if task_id:
        task_id_var.set(task_id)


@worker_shutdown.connect
def handle_worker_shutdown(**kwargs):
    logger.info("Celery worker shutting down — waiting for in-flight tasks to finish")


try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            integrations=[CeleryIntegration()],
            traces_sample_rate=0.1 if settings.environment == "production" else 1.0,
        )
except ImportError:
    pass


__all__ = ["celery_app"]
