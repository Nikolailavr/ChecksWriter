import asyncio
import os

from app.parser.main import Parser
from app.celery.celery_app import celery_app
from core import settings
from core.services.images import ImageService
from core.services.receipts import ReceiptService


@celery_app.task(bind=True)
def process_check(
    self,
    filename: str,
    telegram_id: int,
    category: str,
):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.check(filename)

        if not isinstance(result, dict):
            raise ValueError("Parser должен возвращать словарь")

        # Сохраняем результаты в БД
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            ReceiptService.save_receipt(
                data=result,
                telegram_id=telegram_id,
                category=category,
            )
        )

        os.remove(settings.uploader.DIR / filename)

        loop.run_until_complete(ImageService.delete(filename=filename))
        return {"status": "success", "result": result, "image_path": filename}
    except Exception as e:
        self.retry(exc=e, countdown=60)
