import logging

from aiogram import F, Router, Dispatcher
from aiogram.types import CallbackQuery

from app.bot.keyboards.user import show_receipts, build_receipt_action_keyboard
from core.services.receipts import ReceiptService

logger = logging.getLogger(__name__)
router = Router()


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


def register_users_receipts_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)