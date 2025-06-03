from celery import Celery


from core import settings

celery_app = Celery(
    "app.celery.celery_app",
    broker=settings.celery.BROKER_URL,
    backend=settings.celery.RESULT_BACKEND,
    include=["app.celery.tasks"],
    broker_connection_retry_on_startup=True,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
