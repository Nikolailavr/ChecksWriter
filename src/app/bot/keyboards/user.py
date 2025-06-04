from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from core.database.models import Receipt

PER_PAGE = 6
RECEIPTS_PER_PAGE = 4  # 4 ряда по 1 чеку


async def show_categories(
    message: Message, categories: list[str], page: int, edit: bool = False
):
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_page_categories = categories[start:end]

    keyboard: list[list[InlineKeyboardButton]] = []

    # Кнопки категорий — 2 в ряд (3 ряда максимум)
    for i in range(0, len(current_page_categories), 2):
        row = [
            InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}:0")
            for cat in current_page_categories[i : i + 2]
        ]
        keyboard.append(row)

    # Ряд пагинации
    pagination_buttons = []
    if start > 0:
        pagination_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cats:{page - 1}")
        )
    if end < len(categories):
        pagination_buttons.append(
            InlineKeyboardButton(text="➡️ Далее", callback_data=f"cats:{page + 1}")
        )
    if pagination_buttons:
        keyboard.append(pagination_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit:
        # редактируем сообщение с клавиатурой
        await message.edit_text("Выберите категорию:", reply_markup=markup)
    else:
        # отправляем новое сообщение
        await message.answer("Выберите категорию:", reply_markup=markup)


async def show_receipts(
    message: Message,
    receipts: list[Receipt],
    category: str,
    page: int,
    edit: bool = False,
):
    start = page * RECEIPTS_PER_PAGE
    end = start + RECEIPTS_PER_PAGE
    current_page_receipts = receipts[start:end]

    keyboard: list[list[InlineKeyboardButton]] = []

    # 4 ряда по 1 кнопке с чеком
    for receipt in current_page_receipts:
        date_str = receipt.date_time.strftime("%d.%m.%Y %H:%M")
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=date_str, callback_data=f"r:{receipt.receipt_id}"
                )
            ]
        )

    # Пагинация
    pagination_buttons = []
    if start > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"receipts:{category}:{page - 1}"
            )
        )
    if end < len(receipts):
        pagination_buttons.append(
            InlineKeyboardButton(
                text="➡️ Далее", callback_data=f"receipts:{category}:{page + 1}"
            )
        )
    if pagination_buttons:
        keyboard.append(pagination_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit:
        await message.edit_text(f"Чеки в категории «{category}»", reply_markup=markup)
    else:
        await message.answer(f"Чеки в категории «{category}»:", reply_markup=markup)
