import logging
import os
import uuid
from typing import Dict

from aiogram import Router, F, Dispatcher, types
from app.celery.tasks import process_check

from core import settings
from core.services.images import ImageService

logger = logging.getLogger(__name__)
router = Router()

IMAGE_FOLDER = settings.uploader.DIR

# Временное хранилище для ожидания категорий
user_states: Dict[int, str] = {}


@router.message(F.photo)
async def handle_photo(msg: types.Message):
    # Создаем папку для изображений, если ее нет
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

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
    task = process_check.delay(filepath)
    logger.info(f"Изображение сохранено. Обработка начата (ID задачи: {task.id})")

    # Запоминаем файл и просим категорию
    user_states[msg.from_user.id] = filename
    await msg.answer("Введите название категории для этого чека:")


@router.message(F.text)
async def handle_category(message: types.Message):
    if message.from_user.id not in user_states:
        return

    filename = user_states.pop(message.from_user.id)
    category_name = message.text.strip()

    await ImageService.update(
        filename=filename,
        category=category_name,
    )


def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
