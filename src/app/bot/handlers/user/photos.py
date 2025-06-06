import logging
import os
import uuid

from aiogram import F, Dispatcher, Router
from aiogram.types import Message

from app.celery.tasks import process_check
from core import settings
from core.redis import async_redis_client

IMAGE_FOLDER = settings.uploader.DIR

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.photo)
async def handle_photo(msg: Message):
    # Генерируем уникальное имя файла
    file_id = msg.photo[-1].file_id
    file = await msg.bot.get_file(file_id)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    # Сохраняем изображение
    logger.info(f"Сохраняем файл: {filepath}")
    await msg.bot.download_file(file.file_path, filepath)

    # Сохраняем базовую информацию в Redis
    redis_key = f"receipt:{filename}"
    await async_redis_client.hset(
        redis_key,
        mapping={
            "telegram_id": msg.from_user.id,
            "category": "Общие",
        },
    )
    await async_redis_client.expire(redis_key, 600)  # TTL 10 минут
    task = process_check.delay(filename)
    logger.info(f"Изображение сохранено. Обработка начата (ID задачи: {task.id})")
    await msg.answer("Введите название категории для этого чека:")


@router.message(F.text)
async def handle_category(msg: Message):
    keys = await async_redis_client.keys("receipt:*")
    target_key = None

    for key in keys:
        telegram_id = await async_redis_client.hget(key, "telegram_id")
        if telegram_id == str(msg.from_user.id):
            target_key = key
            break

    if not target_key:
        await msg.answer("Чек не найден, начните с загрузки фото.")
        return

    category = msg.text.strip()
    await async_redis_client.hset(target_key, "category", category)

    await msg.answer("🗳 Обработываю данные...")


def register_users_photos_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
