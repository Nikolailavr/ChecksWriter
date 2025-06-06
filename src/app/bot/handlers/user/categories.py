import logging

from aiogram import F, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

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


@router.callback_query(F.data.startswith("new_cat:"))
async def handle_new_category_request(callback: CallbackQuery, state: FSMContext):
    receipt_id = int(callback.data.split(":")[1])
    await state.set_state(ChangeCategoryState.new_category)
    await state.update_data(receipt_id=receipt_id)
    await callback.message.edit_text("Введите название новой категории:")


@router.message(ChangeCategoryState.new_category)
async def handle_new_category_input(message: Message, state: FSMContext):
    new_cat = message.text.strip()
    data = await state.get_data()
    receipt_id = data["receipt_id"]

    # Сохраняем новую категорию в чек
    await ReceiptService.update_category(receipt_id, new_cat)
    await state.clear()
    await message.answer(f"✅ Категория обновлена на <b>{new_cat}</b>.")


@router.callback_query(F.data.startswith("set_cat:"))
async def handle_set_category(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    receipt_id = int(parts[1])
    new_category = parts[2]

    # Обновление категории (нужен соответствующий метод в ReceiptService)
    await ReceiptService.update_category(receipt_id, new_category)
    await state.clear()
    await callback.message.edit_text(f"✅ Категория обновлена на {new_category}.")


def register_users_categories_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
