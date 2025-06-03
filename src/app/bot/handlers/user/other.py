import logging
import os
import uuid
from typing import Dict

from aiogram import Router, F, Dispatcher, types
from app.celery.tasks import process_check
from app.parser.main import Parser

from core import settings
from core.services.images import ImageService
from core.services.receipts import ReceiptService

logger = logging.getLogger(__name__)
router = Router()

IMAGE_FOLDER = settings.uploader.DIR

# Временное хранилище для ожидания категорий
user_states: Dict[int, str] = {}


@router.message(F.photo)
async def handle_photo(msg: types.Message):
    # Генерируем уникальное имя файла
    file_id = msg.photo[-1].file_id
    file = await msg.bot.get_file(file_id)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    # Сохраняем изображение
    await msg.bot.download_file(file.file_path, filepath)

    await ImageService.get_or_create(
        telegram_id=msg.from_user.id,
        filename=filename,
    )

    # Запускаем задачу Celery
    # task = process_check.delay(filepath)
    # logger.info(f"Изображение сохранено. Обработка начата (ID задачи: {task.id})")

    # Запоминаем файл и просим категорию
    user_states[msg.from_user.id] = filename
    await msg.answer("Введите название категории для этого чека:")


@router.message(F.text)
async def handle_category(msg: types.Message):
    if msg.from_user.id not in user_states:
        return

    filename = user_states.pop(msg.from_user.id)
    category_name = msg.text.strip()

    await ImageService.update(
        filename=filename,
        category=category_name,
    )

    parser = Parser()
    try:
        result = parser.check(filename)
        await ReceiptService.save_receipt(
            data=result,
            telegram_id=msg.from_user.id,
            category=category_name,
        )
    except Exception as ex:
        logger.error(ex)
    finally:
        os.remove(settings.uploader.DIR / filename)
        await ImageService.delete(filename=filename)


def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
