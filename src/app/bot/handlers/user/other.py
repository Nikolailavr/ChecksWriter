import logging
import os
import uuid

from aiogram import Router, F, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from app.bot.keyboards.user import (
    show_categories,
    show_receipts,
    build_receipt_action_keyboard,
    build_category_keyboard,
)
from app.celery.tasks import process_check

from core import settings
from core.redis import async_redis_client
from core.services.receipts import ReceiptService

logger = logging.getLogger(__name__)
router = Router()

IMAGE_FOLDER = settings.uploader.DIR


class ChangeCategoryState:
    choosing = State()


@router.message(F.photo)
async def handle_photo(msg: types.Message):
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


@router.callback_query(F.data.startswith("cats:"))
async def paginate_categories(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    categories = await ReceiptService.get_categories(callback.from_user.id)
    # Редактируем сообщение, выводим нужную страницу категорий
    await show_categories(callback.message, categories, page, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_receipts_callback(callback: CallbackQuery):
    _, category, page_str = callback.data.split(":")
    page = int(page_str)
    receipts = await ReceiptService.get_receipts(
        telegram_id=callback.from_user.id,
        category=category,
    )
    await show_receipts(callback.message, receipts, category, page, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("receipts:"))
async def paginate_receipts(callback: CallbackQuery):
    _, category, page_str = callback.data.split(":")
    page = int(page_str)
    receipts = await ReceiptService.get_receipts(
        telegram_id=callback.from_user.id,
        category=category,
    )
    await show_receipts(callback.message, receipts, category, page, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("receipt:"))
async def receipt_action_menu(callback: CallbackQuery):
    receipt_id = int(callback.data.split(":")[1])
    keyboard = build_receipt_action_keyboard(receipt_id)
    await callback.message.edit_text(
        "Выберите действие для чека:", reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view:"))
async def show_receipt_items(callback: CallbackQuery):
    receipt_id = int(callback.data.split(":")[1])
    items = await ReceiptService.get_receipt(receipt_id)
    if not items:
        await callback.message.answer("Покупки не найдены.")
    else:
        lines = ["🧾 Покупки:"]
        for item in items:
            lines.append(
                f"{item.name}\n{item.price / 100:.2f} ₽ × {item.quantity} = {item.sum / 100:.2f} ₽\n"
            )
        await callback.message.answer("\n".join(lines))
    await callback.answer()


# --- Обработчик кнопки "Изменить категорию" ---
@router.callback_query(F.data.startswith("change_cat:"))
async def handle_change_category(callback: CallbackQuery, state: FSMContext):
    receipt_id = int(callback.data.split(":")[1])
    telegram_id = callback.from_user.id

    categories = await ReceiptService.get_categories(telegram_id)
    if not categories:
        await callback.message.answer("❌ У вас ещё нет категорий.")
        return

    await state.set_state(ChangeCategoryState.choosing)
    await state.update_data(receipt_id=receipt_id)

    await callback.message.edit_text(
        "🔽 Выберите новую категорию:",
        reply_markup=build_category_keyboard(receipt_id, categories),
    )


# --- Обработчик установки новой категории ---
@router.callback_query(F.data.startswith("set_cat:"))
async def handle_set_category(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    receipt_id = int(parts[1])
    new_category = parts[2]

    # Обновление категории (нужен соответствующий метод в ReceiptService)
    await ReceiptService.update_category(receipt_id, new_category)

    await state.clear()
    await callback.message.edit_text(
        f"✅ Категория обновлена на <b>{new_category}</b>."
    )


@router.callback_query(F.data.startswith("delete:"))
async def delete_receipt(callback: CallbackQuery):
    receipt_id = int(callback.data.split(":")[1])
    await ReceiptService.delete_receipt(receipt_id)
    await callback.message.edit_text("✅ Чек удалён.")
    await callback.answer()


@router.message(F.text)
async def handle_category(msg: types.Message):
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


def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
