import asyncio

from app.parser.main import Parser
from app.celery.celery_app import celery_app
from core.services.receipts import ReceiptService


@celery_app.task(bind=True)
def process_check(self, image_path: str):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.check(image_path)

        if not isinstance(result, dict):
            raise ValueError("Parser должен возвращать словарь")

        # Сохраняем результаты в БД
        asyncio.run(ReceiptService.save_receipt(result))

        return {"status": "success", "result": result, "image_path": image_path}
    except Exception as e:
        self.retry(exc=e, countdown=60)
