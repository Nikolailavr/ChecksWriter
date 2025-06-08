import logging
import os
import uuid

from aiogram import F, Dispatcher, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.user import build_category_keyboard
from app.celery.tasks import process_check
from core import settings
from core.redis import async_redis_client
from core.services.receipts import ReceiptService

IMAGE_FOLDER = settings.uploader.DIR

logger = logging.getLogger(__name__)
router = Router()


class ReceiptUploadState(StatesGroup):
    waiting_for_category = State()
    entering_new_category = State()


@router.message(F.photo)
async def handle_photo(msg: Message, state: FSMContext):
    file_id = msg.photo[-1].file_id
    file = await msg.bot.get_file(file_id)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    # Сохраняем в Redis
    redis_key = f"receipt:{filename}"
    await async_redis_client.hset(
        redis_key,
        mapping={
            "telegram_id": msg.from_user.id,
            "category": "Общие",
            "message_id": msg.message_id,
        },
    )
    await async_redis_client.expire(redis_key, 600)

    await state.set_state(ReceiptUploadState.waiting_for_category)
    await state.update_data(receipt_key=redis_key)

    # Получаем категории
    categories = await ReceiptService.get_categories(msg.from_user.id)
    keyboard = build_category_keyboard(categories)

    # Отправляем сообщение с клавиатурой
    await msg.answer(
        "Введите категорию для этого чека или выберите из списка:",
        reply_markup=keyboard,
    )

    logger.info(f"Сохраняем файл: {filepath}")
    await msg.bot.download_file(file.file_path, filepath)

    # Запускаем обработку чека
    task = process_check.delay(filename)
    logger.info(f"Обработка запущена (ID задачи: {task.id})")


@router.callback_query(
    StateFilter(ReceiptUploadState.waiting_for_category),
    F.data.startswith("select_cat:"),
)
async def handle_category_selection(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    # Обработка выбранной категории
    await callback.message.answer(
        f"✅ Категория выбрана: {category}\n🗳 Обрабатываю данные..."
    )
    await state.clear()  # или переход в следующее состояние


# @router.callback_query(F.data == "new_cat")
@router.callback_query(
    StateFilter(ReceiptUploadState.waiting_for_category),
    F.data == "new_cat",
)
async def handle_new_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название новой категории:")
    await state.set_state(ReceiptUploadState.entering_new_category)


@router.message(ReceiptUploadState.entering_new_category)
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
    await msg.answer(f"✅ Категория выбрана: {category}\n🗳 Обрабатываю данные...")


def register_users_photos_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
