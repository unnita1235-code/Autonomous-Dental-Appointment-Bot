from app.core.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> str:
    return "pong"


__all__ = ["celery_app", "ping"]
