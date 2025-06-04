import asyncio
import logging
import os

from app.parser.main import Parser
from app.celery.celery_app import celery_app
from core import settings
from core.services.images import ImageService
from core.services.receipts import ReceiptService
from celery.signals import task_success, task_failure

log = logging.getLogger(__name__)


def do_other_check(data: dict):
    asyncio.run(async_do_other(data))


async def async_do_other(data: dict):
    await ReceiptService.save_receipt(
        data=data["result"],
        telegram_id=data["telegram_id"],
        category=data["category"],
    )
    os.remove(settings.uploader.DIR / data["filename"])
    await ImageService.delete(filename=data["filename"])
    from app.bot.main import send_msg

    await send_msg(chat_id=data["chat_id"], text="✅ Данные чека успешно внесены!")


@celery_app.task(bind=True)
def process_check(self, data: dict):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.check(data["filename"])
        if not isinstance(result, dict):
            raise ValueError("Parser должен возвращать словарь")
        data["result"] = result
        return {"status": "success", "data": data}
    except Exception as e:
        self.retry(exc=e, countdown=60)


# Успешное выполнение задачи
@task_success.connect
def task_success_handler(
    sender=None,
    result=None,
    **kwargs,
):
    log.info(f"✅ Задача '{sender.name}' выполнена успешно")
    do_other_check(result.get("data", dict))


# Ошибка при выполнении задачи
@task_failure.connect
def task_failure_handler(
    sender=None,
    task_id=None,
    exception=None,
    args=None,
    kwargs=None,
    traceback=None,
    einfo=None,
    **other,
):
    log.error(f"❌ Задача '{sender.name}' завершилась с ошибкой: {exception}")
