from celery import Celery
from app.parser.main import Parser

from core import settings

app = Celery(
    "tasks",
    broker=settings.celery.BROKER_URL,
    backend=settings.celery.RESULT_BACKEND,
)


@app.task(bind=True)
def process_check(self, image_path: str):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.check(image_path)

        if not isinstance(result, dict):
            raise ValueError("Parser должен возвращать словарь")

            # Сохраняем результаты в БД
        # await save_parsed_data(image_path, result)

        return {"status": "success", "result": result, "image_path": image_path}
    except Exception as e:
        self.retry(exc=e, countdown=60)
