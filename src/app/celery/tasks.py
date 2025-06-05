import asyncio
import logging
import os

from sqlalchemy.exc import SQLAlchemyError

from app.parser.exceptions import BadQRCodeError
from app.parser.main import Parser
from app.celery.celery_app import celery_app
from core import settings
from core.config import redis_client
from core.services.receipts import ReceiptService
from celery.signals import task_success, task_failure

logger = logging.getLogger(__name__)


@celery_app.task
def success_check(data: dict):
    from app.bot.main import send_msg

    user_data = redis_client.hgetall(f"receipt:{data.get("filename")}")
    chat_id = int(user_data["telegram_id"])
    try:
        ReceiptService.save_receipt(
            data=data["result"],
            telegram_id=chat_id,
            category=user_data["category"],
        )
    except SQLAlchemyError as ex:
        logger.error(f"[ERROR] {ex}")
        send_msg(chat_id=chat_id, text="❌ Ошибка, чек уже внесен")
    else:
        send_msg(chat_id=chat_id, text="✅ Данные чека успешно внесены!")
    finally:
        redis_client.delete(f"receipt:{data.get("filename")}")


@celery_app.task
def failure_check(data: dict):
    from app.bot.main import send_msg

    try:
        user_data = redis_client.hgetall(f"receipt:{data.get("filename")}")
        chat_id = int(user_data["telegram_id"])
        send_msg(chat_id=chat_id, text="❌ Ошибка, не удалось распознать!")
    finally:
        redis_client.delete(f"receipt:{data.get("filename")}")


@celery_app.task(bind=True)
def process_check(self, filename: str):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.check(filename)
        if not isinstance(result, dict):
            raise ValueError("Parser должен возвращать словарь")
        return {"status": "success", "result": result, "filename": filename}
    except FileExistsError:
        ...
    except BadQRCodeError:
        raise BadQRCodeError("Не удалось распознать QR-код")
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=2)
    finally:
        remove_file(filename)


def remove_file(filename: str):
    try:
        os.remove(os.path.abspath(settings.uploader.DIR / filename))
    except FileNotFoundError as ex:
        logger.error(f"[ERROR] File not found {settings.uploader.DIR / filename}")


# Успешное выполнение задачи
@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    logger.info(f"✅ Задача '{sender.name}' выполнена успешно")

    # Проверка результата от process_check
    if sender.name == "app.celery.tasks.process_check" and isinstance(result, dict):
        parsed = result.get("result")
        filename = result.get("filename")
        if parsed and filename:
            success_check.delay(data={"result": parsed, "filename": filename})


# Ошибка при выполнении задачи
@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, args=None, **kwargs
):
    logger.error(f"❌ Задача '{sender.name}' завершилась с ошибкой: {exception}")

    if sender.name == "app.celery.tasks.process_check" and args:
        failure_check.delay(data=args[0])
