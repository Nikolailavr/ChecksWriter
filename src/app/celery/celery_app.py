from celery import Celery


from core import settings

celery_app = Celery(
    "worker",
    broker=settings.celery.BROKER_URL,
    backend=settings.celery.RESULT_BACKEND,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
