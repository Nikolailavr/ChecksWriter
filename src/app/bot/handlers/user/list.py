from aiogram import Router, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.services.receipts import ReceiptService

router = Router()

PER_PAGE = 6


@router.message(Command("list"))
async def list_categories(msg: Message):
    categories = await ReceiptService.get_categories(msg.from_user.id)
    await show_categories(msg, categories, page=0)


async def show_categories(message: Message, categories: list[str], page: int):
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_page_categories = categories[start:end]

    keyboard: list[list[InlineKeyboardButton]] = []

    # Группируем категории по 2 в ряд (3 ряда максимум)
    for i in range(0, len(current_page_categories), 2):
        row = [
            InlineKeyboardButton(
                text=cat,
                callback_data=f"cat:{cat}:0"
            )
            for cat in current_page_categories[i:i + 2]
        ]
        keyboard.append(row)

    # Добавляем ряд с пагинацией
    pagination_buttons = []
    if start > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", callback_data=f"cats:{page - 1}")
        )
    if end < len(categories):
        pagination_buttons.append(InlineKeyboardButton(
            text="➡️ Далее", callback_data=f"cats:{page + 1}")
        )
    if pagination_buttons:
        keyboard.append(pagination_buttons)

    await message.answer(
        "Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.callback_query(F.data.startswith("cats:"))
async def paginate_categories(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    categories = await ReceiptService.get_categories(callback.from_user.id)

    await callback.message.edit_text("Выберите категорию:")
    await show_categories(callback.message, categories, page)
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_receipts(callback: CallbackQuery):
    _, category, page = callback.data.split(":")
    page = int(page)
    start = page * PER_PAGE
    end = start + PER_PAGE
    builder = InlineKeyboardBuilder()
    receipts = await ReceiptService.get_receipts(
        telegram_id=callback.from_user.id,
        category=category,
    )

    for receipt in receipts[start:end]:
        dt = receipt.date_time.strftime("%d.%m.%Y %H:%M")
        builder.button(text=dt, callback_data=f"r:{receipt.receipt_id}")

    if start > 0:
        builder.button(text="⬅️", callback_data=f"cat:{category}:{page - 1}")
    if end < len(receipts):
        builder.button(text="➡️", callback_data=f"cat:{category}:{page + 1}")

    await callback.message.edit_text(f"Чеки категории: {category}")
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("r:"))
async def show_receipt_items(callback: CallbackQuery):
    receipt_id = int(callback.data.split(":")[1])
    items = await ReceiptService.get_receipt(receipt_id)
    text = "🧾 Покупки:\n\n"
    for item in items:
        text += f"{item.name} — {item.price * 0.01} × {item.quantity} = {item.sum * 0.01}\n"

    await callback.message.edit_text(text)
    await callback.answer()


def register_users_list_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
