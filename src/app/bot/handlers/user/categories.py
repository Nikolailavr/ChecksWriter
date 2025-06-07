import csv
import io
import logging

from aiogram import F, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from app.bot.keyboards.user import (
    show_categories,
    show_receipts,
    build_category_keyboard,
)
from core.services.receipts import ReceiptService

logger = logging.getLogger(__name__)
router = Router()


class ChangeCategoryState(StatesGroup):
    choosing = State()
    new_category = State()


@router.callback_query(F.data.startswith("cats:"))
async def paginate_categories(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    categories = await ReceiptService.get_categories(callback.from_user.id)
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


@router.callback_query(F.data.startswith("change_cat:"))
async def handle_change_category(callback: CallbackQuery, state: FSMContext):
    receipt_id = callback.data.split(":")[1]
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


@router.callback_query(F.data.startswith("new_cat:"))
async def handle_new_category_request(callback: CallbackQuery, state: FSMContext):
    receipt_id = callback.data.split(":")[1]
    await state.set_state(ChangeCategoryState.new_category)
    await state.update_data(receipt_id=receipt_id)
    await callback.message.edit_text("Введите название новой категории:")


@router.message(ChangeCategoryState.new_category)
async def handle_new_category_input(message: Message, state: FSMContext):
    new_cat = message.text.strip()
    data = await state.get_data()
    receipt_id = data["receipt_id"]
    logger.info(f"{receipt_id=} | {new_cat=}")
    await ReceiptService.update_category(receipt_id, new_cat)
    await state.clear()
    await message.answer(f"✅ Категория обновлена на {new_cat}.")


@router.callback_query(F.data.startswith("set_cat:"))
async def handle_set_category(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    receipt_id = parts[1]
    new_category = parts[2]
    await ReceiptService.update_category(receipt_id, new_category)
    await state.clear()
    await callback.message.edit_text(f"✅ Категория обновлена на {new_category}.")


@router.callback_query(F.data.startswith("export_cat:"))
async def export_category_receipts(callback: CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) != 2:
        await callback.answer("⚠ Неверный формат данных.")
        return

    category = parts[1]
    telegram_id = callback.from_user.id

    receipts = await ReceiptService.get_receipts(telegram_id, category)
    if not receipts:
        await callback.message.answer("❌ Нет чеков в этой категории.")
        await callback.answer()
        return

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Date",
            "Time",
            "Name",
            "Quantity",
            "Price",
            "Sum",
            "Retail Place",
            "Address",
            "Receipt ID",
        ]
    )

    for receipt in receipts:
        date_str = receipt.date_time.strftime("%d-%m-%Y")
        time_str = receipt.date_time.strftime("%H:%M:%S")

        for item in receipt.items:
            writer.writerow(
                [
                    date_str,
                    time_str,
                    item.name,
                    item.quantity,
                    f"{item.price / 100:.2f}",
                    f"{item.sum / 100:.2f}",
                    receipt.retail_place or "",
                    receipt.address or "",
                    receipt.receipt_id,
                ]
            )

    # Подготовка CSV-файла
    output.seek(0)
    file = BufferedInputFile(
        output.read().encode("utf-8"), filename=f"category_{category}.csv"
    )
    await callback.message.answer_document(
        file, caption=f"📄 Чеки из категории «{category}»"
    )
    await callback.answer()


def register_users_categories_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
