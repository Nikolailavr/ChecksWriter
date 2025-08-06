from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.bot.handlers.other import logger
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
        callback_data = f"receipt:{receipt.receipt_id}"
        logger.info(f"{callback_data=}")
        keyboard.append(
            [InlineKeyboardButton(text=date_str, callback_data=callback_data)]
        )

    # Пагинация
    pagination_buttons = [
        InlineKeyboardButton(
            text="📤 Экспорт в Excel", callback_data=f"export_cat:{category}"
        )
    ]
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


def build_receipt_action_keyboard(receipt_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👁 Просмотр", callback_data=f"view:{receipt_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬇ Скачать", callback_data=f"download:{receipt_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить", callback_data=f"delete:{receipt_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏ Изменить категорию",
                    callback_data=f"change_cat:{receipt_id}",
                )
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="cats:0")],
        ]
    )



# --- Кнопки выбора категории ---
def build_category_keyboard_change(
    receipt_id: str,
    categories: list[str],
) -> InlineKeyboardMarkup:
    # Формируем кнопки по 2 в строку
    keyboard = [
        [
            InlineKeyboardButton(text=cat1, callback_data=f"set_cat:{receipt_id}:{cat1}"),
            InlineKeyboardButton(text=cat2, callback_data=f"set_cat:{receipt_id}:{cat2}")
        ] if cat2 else [InlineKeyboardButton(text=cat1, callback_data=f"set_cat:{receipt_id}:{cat1}")]
        for cat1, cat2 in zip(categories[::2], categories[1::2] + [None] if len(categories) % 2 else categories[1::2])
    ]
    keyboard.append([
        InlineKeyboardButton(text="➕ Новая категория", callback_data=f"new_cat:{receipt_id}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"receipt:{receipt_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_category_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text=cat1, callback_data=f"select_cat:{cat1}"),
            InlineKeyboardButton(text=cat2, callback_data=f"select_cat:{cat2}")
        ] if cat2 else [InlineKeyboardButton(text=cat1, callback_data=f"select_cat:{cat1}")]
        for cat1, cat2 in zip(categories[::2], categories[1::2] + [None] if len(categories) % 2 else categories[1::2])
    ]
    keyboard.append([
        InlineKeyboardButton(text="➕ Новая категория", callback_data="new_cat")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
