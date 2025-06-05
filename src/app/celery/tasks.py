import asyncio
import logging
import os

from sqlalchemy.exc import SQLAlchemyError

from app.parser.exceptions import BadQRCodeError
from app.parser.main import Parser
from app.celery.celery_app import celery_app
from core import settings
from core.services.receipts import ReceiptService
from celery.signals import task_success, task_failure

log = logging.getLogger(__name__)


@celery_app.task
def success_check(data: dict):
    asyncio.run(async_success_check(data))


async def async_success_check(data: dict):
    from app.bot.main import send_msg

    try:
        await ReceiptService.save_receipt(
            data=data["result"],
            telegram_id=data["telegram_id"],
            category=data["category"],
        )
    except SQLAlchemyError as ex:
        log.error(f"[ERROR] {ex}")
        await send_msg(chat_id=data["chat_id"], text="❌ Ошибка, чек уже внесен")
    else:
        await send_msg(chat_id=data["chat_id"], text="✅ Данные чека успешно внесены!")


@celery_app.task
def failure_check(data: dict):
    asyncio.run(async_failure_check(data))


async def async_failure_check(data: dict):
    from app.bot.main import send_msg

    await send_msg(chat_id=data["chat_id"], text="❌ Ошибка, не удалось распознать!")


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
    except FileExistsError:
        ...
    except BadQRCodeError:
        raise BadQRCodeError("Не удалось распознать QR-код")
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=2)
    finally:
        remove_file(data)


def remove_file(data: dict):
    try:
        os.remove(os.path.abspath(settings.uploader.DIR / data["filename"]))
    except FileNotFoundError as ex:
        log.error(f"[ERROR] File not found {settings.uploader.DIR / data["filename"]}")


# Успешное выполнение задачи
@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    log.info(f"✅ Задача '{sender.name}' выполнена успешно")

    # Проверка результата от process_check
    if sender.name == "app.celery.tasks.process_check" and isinstance(result, dict):
        data = result.get("data")
        if data:
            success_check.delay(data=data)


# Ошибка при выполнении задачи
@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, args=None, **kwargs
):
    log.error(f"❌ Задача '{sender.name}' завершилась с ошибкой: {exception}")

    if sender.name == "app.celery.tasks.process_check" and args:
        failure_check.delay(data=args[0])
