from app.celery.celery_app import celery_app

# импорт задач, чтобы Celery их зарегистрировал
import celery_app.tasks  # noqa
