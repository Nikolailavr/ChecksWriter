import logging
import os

from sqlalchemy.exc import SQLAlchemyError

from app.parser.exceptions import BadQRCodeError
from app.parser.main import Parser
from app.celery.celery_app import celery_app
from core import settings
from core.redis import redis_client
from app.celery.helper import CeleryHelper
from core.services.receipts import ReceiptService
from celery.signals import task_success, task_failure

logger = logging.getLogger(__name__)

cel_helper = CeleryHelper()


def success_check(data: dict):
    from app.bot.main import send_msg

    filename = data.get("filename")
    category = None
    telegram_id = None
    message_id = None
    try:
        logger.info(f"Забираем данные из redis для файла: {filename}")
        user_data = redis_client.hgetall(f"receipt:{filename}")
        category = user_data.get("category")
        if not user_data:
            logger.warning(f"Данные для receipt:{filename} не найдены в Redis.")
            return

        telegram_id_str = user_data.get("telegram_id")
        message_id = user_data.get("message_id")
        if telegram_id_str:
            telegram_id = int(telegram_id_str)
        logger.info("Сохраняем в Postgres")
        cel_helper.run(
            ReceiptService.save_receipt(
                data=data["result"],
                telegram_id=telegram_id,
                category=category,
            )
        )
    except SQLAlchemyError as ex:
        logger.error(f"[ERROR] {ex}")
        text = "❌ Ошибка, чек уже внесен"
        if category:
            text += f" в категорию {category}"
        logger.info(f"Отправка сообщения: {text}")
        cel_helper.run(
            send_msg(
                chat_id=telegram_id,
                text=text,
                message_id=message_id,
            )
        )
    else:
        text = f"✅ Данные чека внесены в категорию {category}"
        logger.info(f"Отправка сообщения: {text}")
        cel_helper.run(
            send_msg(
                chat_id=telegram_id,
                text=text,
                message_id=message_id,
            )
        )
    finally:
        redis_client.delete(f"receipt:{filename}")


@celery_app.task()
def failure_check(filename: str):
    from app.bot.main import send_msg

    try:
        logger.info(f"Забираем данные из redis для файла: {filename}")
        user_data = redis_client.hgetall(f"receipt:{filename}")
        if not user_data:
            logger.warning(f"Данные для receipt:{filename} не найдены в Redis.")
            return
        message_id = user_data.get("message_id")
        chat_id_str = user_data.get("telegram_id")
        if chat_id_str:
            chat_id = int(chat_id_str)
            logger.info(
                f"Отправка сообщения для chat_id {chat_id}: ❌ Ошибка, не удалось распознать {filename}!"
            )
            cel_helper.run(
                send_msg(
                    chat_id=chat_id,
                    text=f"❌ Ошибка, не удалось распознать файл!",
                    message_id=message_id,
                )
            )
        else:
            logger.warning(f"telegram_id не найден в user_data для receipt:{filename}")

    except Exception as e:
        logger.error(f"Произошла ошибка в failure_check для {filename}: {e}")
    finally:
        logger.info(f"Удаляем ключ receipt:{filename} из Redis.")
        redis_client.delete(f"receipt:{filename}")


@celery_app.task(bind=True)
def process_check(self, filename: str):
    """Задача Celery для обработки чека"""
    try:
        parser = Parser()
        result = parser.check(filename)
        if not isinstance(result, dict):
            raise ValueError("Parser должен возвращать словарь")
        success_check(data={"result": result, "filename": filename})
        return {"status": "success", "result": result, "filename": filename}
    except FileNotFoundError as e:
        logger.warning(f"Файл {filename} не найден парсером: {e}")
        raise
    # except BadQRCodeError as e:
    #     logger.warning(f"Не удалось распознать QR-код для {filename}: {e}")
    #     raise
    except Exception as e:
        logger.error(
            f"Общая ошибка при обработке {filename}: {e}, попытка {self.request.retries + 1} из {self.max_retries}"
        )
        self.retry(exc=e, countdown=5, max_retries=2)


@celery_app.task
def download_receipt(receipt_id: str):
    try:
        parser = Parser()
        result = parser.download(receipt_id)
        if result.get("status") == "success":
            redis_data = redis_client.hgetall(receipt_id)
            image_path = redis_data.get("filename")
            chat_id_str = redis_data.get("telegram_id")
            from app.bot.main import send_image
            cel_helper.run(
                send_image(
                    chat_id=chat_id_str,
                    image_path=image_path,
                )
            )
            redis_client.delete(receipt_id)
        return result
    except Exception as ex:
        raise ex



def remove_file(filepath: str):
    try:
        os.remove(os.path.abspath(filepath))
    except FileNotFoundError as ex:
        logger.error(f"[ERROR] File not found {filepath}")


# Успешное выполнение задачи
@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    logger.info(f"✅ Задача '{sender.name}' выполнена успешно")
    if sender.name == "app.celery.tasks.process_check":
        remove_file(settings.uploader.DIR / result.get("filename"))
    if sender.name == "app.celery.tasks.download_receipt":
        remove_file(result.get("filename"))



# Ошибка при выполнении задачи
@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, args=None, **kwargs
):
    logger.error(f"❌ Задача '{sender.name}' завершилась с ошибкой: {exception}")

    if sender.name == "app.celery.tasks.process_check" and args:
        failure_check.delay(filename=args[0])
