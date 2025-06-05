import logging
import os
import uuid
from typing import Dict

from aiogram import Router, F, Dispatcher, types
from aiogram.types import CallbackQuery

from app.bot.keyboards.user import (
    show_categories,
    show_receipts,
    build_receipt_action_keyboard,
)
from app.celery.tasks import process_check
from app.parser.main import Parser

from core import settings
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
    logger.info(f"Сохраняем файл: {filepath}")
    await msg.bot.download_file(file.file_path, filepath)

    # Запоминаем файл и просим категорию
    user_states[msg.from_user.id] = filename
    await msg.answer("Введите название категории для этого чека:")


@router.callback_query(F.data.startswith("cats:"))
async def paginate_categories(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    categories = await ReceiptService.get_categories(callback.from_user.id)
    logger.info(f"{categories=}")
    if len(categories) == 0:
        await callback.message.answer("Категории не найдены.")
    else:
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


@router.callback_query(F.data.startswith("delete:"))
async def delete_receipt(callback: CallbackQuery):
    receipt_id = int(callback.data.split(":")[1])
    await ReceiptService.delete_receipt(receipt_id)
    await callback.message.edit_text("✅ Чек удалён.")
    await callback.answer()


@router.message(F.text)
async def handle_category(msg: types.Message):
    if msg.from_user.id not in user_states:
        return
    await msg.answer("🗳 Обработываю данные...")
    filename = user_states.pop(msg.from_user.id)
    category_name = msg.text.strip()

    user_data = {
        "chat_id": msg.chat.id,
        "filename": filename,
        "telegram_id": msg.from_user.id,
        "category": category_name,
    }
    # Запускаем задачу Celery
    task = process_check.delay(user_data)
    logger.info(f"Изображение сохранено. Обработка начата (ID задачи: {task.id})")

    # parser = Parser()
    # try:
    #     result = parser.check(filename)
    #     await ReceiptService.save_receipt(
    #         data=result,
    #         telegram_id=msg.from_user.id,
    #         category=category_name,
    #     )
    #     await msg.answer("✅ Данные чека успешно внесены!")
    # except Exception as ex:
    #     logger.error(ex)
    #     await msg.answer("❌ Ошибка, не удалось распознать")
    # finally:
    #     os.remove(settings.uploader.DIR / filename)


def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
