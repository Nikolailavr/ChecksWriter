import logging
import os
import uuid

from aiogram import F, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from app.celery.tasks import process_check
from core import settings
from core.redis import async_redis_client

IMAGE_FOLDER = settings.uploader.DIR

logger = logging.getLogger(__name__)
router = Router()


class ReceiptUploadState(StatesGroup):
    waiting_for_category = State()


@router.message(F.photo)
async def handle_photo(msg: Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    file = await msg.bot.get_file(file_id)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    logger.info(f"Сохраняем файл: {filepath}")
    await msg.bot.download_file(file.file_path, filepath)

    # Сохраняем в Redis
    redis_key = f"receipt:{filename}"
    await async_redis_client.hset(
        redis_key,
        mapping={
            "telegram_id": msg.from_user.id,
            "category": "Общие",
        },
    )
    await async_redis_client.expire(redis_key, 600)

    # Устанавливаем состояние и временные данные
    await state.set_state(ReceiptUploadState.waiting_for_category)
    await state.update_data(receipt_key=redis_key)

    task = process_check.delay(filename)
    logger.info(f"Обработка запущена (ID задачи: {task.id})")
    await msg.answer("Введите название категории для этого чека:")


@router.message(ReceiptUploadState.waiting_for_category)
async def handle_category(msg: Message, state: FSMContext):
    data = await state.get_data()
    redis_key = data.get("receipt_key")

    if not redis_key or not await async_redis_client.exists(redis_key):
        await state.clear()
        await msg.answer(
            "⏰ Время на ввод категории истекло. Пожалуйста, загрузите фото заново."
        )
        return

    category = msg.text.strip()
    await async_redis_client.hset(redis_key, "category", category)

    await state.clear()
    await msg.answer("🗳 Обрабатываю данные...")


def register_users_photos_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
