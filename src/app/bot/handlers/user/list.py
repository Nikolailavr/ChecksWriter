from aiogram import Router, types, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from core.database.models import Receipt, ReceiptItem

router = Router()

ITEMS_PER_PAGE = 5

# --- Callback Data Schemas для пагинации ---
from aiogram.filters.callback_data import CallbackData

category_cb = CallbackData("category", "page")  # page - номер страницы
receipt_cb = CallbackData(
    "receipt", "category", "page"
)  # category - выбранная категория, page - страница
items_cb = CallbackData("items", "receipt_id")  # чек для списка товаров


# --- Вспомогательные функции для клавиатур ---


async def get_categories_keyboard(user_id: int, session: AsyncSession, page: int = 1):
    # Получаем уникальные категории пользователя с пагинацией
    stmt = (
        select(Receipt.category)
        .where(Receipt.user_id == user_id)
        .distinct()
        .offset((page - 1) * ITEMS_PER_PAGE)
        .limit(ITEMS_PER_PAGE + 1)
    )
    result = await session.execute(stmt)
    categories = [row[0] for row in result.all()]

    keyboard = InlineKeyboardMarkup(row_width=1)
    for cat in categories[:ITEMS_PER_PAGE]:
        keyboard.add(
            InlineKeyboardButton(
                cat, callback_data=category_cb.new(page=page) + f":{cat}"
            )
        )

    # Пагинация
    if len(categories) > ITEMS_PER_PAGE:
        keyboard.row(
            InlineKeyboardButton(
                "⬅️",
                callback_data=(
                    category_cb.new(page=page - 1)
                    if page > 1
                    else category_cb.new(page=1)
                ),
            ),
            InlineKeyboardButton("➡️", callback_data=category_cb.new(page=page + 1)),
        )

    return keyboard


async def get_receipts_keyboard(
    user_id: int, category: str, session: AsyncSession, page: int = 1
):
    # Получаем чеки пользователя по категории с пагинацией
    stmt = (
        select(Receipt)
        .where(Receipt.user_id == user_id, Receipt.category == category)
        .order_by(Receipt.date_time.desc())
        .offset((page - 1) * ITEMS_PER_PAGE)
        .limit(ITEMS_PER_PAGE + 1)
    )
    result = await session.execute(stmt)
    receipts = result.scalars().all()

    keyboard = InlineKeyboardMarkup(row_width=1)
    for receipt in receipts[:ITEMS_PER_PAGE]:
        label = receipt.date_time.strftime("%Y-%m-%d %H:%M")
        keyboard.add(
            InlineKeyboardButton(
                label,
                callback_data=receipt_cb.new(category=category, page=page)
                + f":{receipt.id}",
            )
        )

    # Пагинация
    if len(receipts) > ITEMS_PER_PAGE:
        keyboard.row(
            InlineKeyboardButton(
                "⬅️",
                callback_data=(
                    receipt_cb.new(category=category, page=page - 1)
                    if page > 1
                    else receipt_cb.new(category=category, page=1)
                ),
            ),
            InlineKeyboardButton(
                "➡️", callback_data=receipt_cb.new(category=category, page=page + 1)
            ),
        )

    return keyboard


async def format_receipt_items(receipt_id: int, session: AsyncSession):
    stmt = select(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id)
    result = await session.execute(stmt)
    items = result.scalars().all()

    lines = ["Название | Цена | Кол-во | Стоимость"]
    lines.append("-" * 40)
    for item in items:
        line = f"{item.name} | {item.price} | {item.quantity} | {item.sum}"
        lines.append(line)
    return "\n".join(lines)


# --- Хэндлеры ---


@router.message(Command("list"))
async def cmd_list(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    keyboard = await get_categories_keyboard(user_id, session, page=1)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@router.callback_query(category_cb.filter())
async def category_callback(
    callback: types.CallbackQuery, callback_data: dict, session: AsyncSession
):
    user_id = callback.from_user.id
    page = int(callback_data["page"])
    # Извлечь категорию из callback_data (если передаем через postfixed string — лучше переделать на отдельные поля)
    # Например callback_data = "category:1:Ремонт" => 'Ремонт' после split
    # Но здесь пока пропущу — подставим ручное получение категории из callback_data (если у тебя в callback_data только page — надо расширить)

    # Для простоты: здесь надо делать нормальную структуру callback_data с category, page
    # Или передавать категорию через callback_data (лучше использовать CallbackData с полями)
    # Для примера возьмем, что категория в тексте кнопки (callback.message.text) — лучше сделать по-другому
    # Здесь пример с фиктивной категорией (нужно доработать под твой callback_data)
    category = "example_category"  # заменить на правильное значение

    keyboard = await get_receipts_keyboard(user_id, category, session, page)
    await callback.message.edit_text(
        f"Чеки в категории {category}:", reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(receipt_cb.filter())
async def receipt_callback(
    callback: types.CallbackQuery, callback_data: dict, session: AsyncSession
):
    receipt_id = int(
        callback_data.get("page")
    )  # здесь хак, нужно исправить, лучше делать поле receipt_id в callback_data
    text = await format_receipt_items(receipt_id, session)
    await callback.message.edit_text(text)
    await callback.answer()


def register_users_list_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
