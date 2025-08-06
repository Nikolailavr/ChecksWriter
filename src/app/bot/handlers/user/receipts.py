import logging

from aiogram import F, Router, Dispatcher
from aiogram.types import CallbackQuery, BufferedInputFile

from app.bot.keyboards.user import show_receipts, build_receipt_action_keyboard
from core.redis import async_redis_client
from core.services.receipts import ReceiptService
from app.celery.tasks import download_receipt

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
    receipt_id = callback.data.split(":")[1]
    keyboard = build_receipt_action_keyboard(receipt_id)
    await callback.message.edit_text(
        "Выберите действие для чека:", reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view:"))
async def show_receipt_items(callback: CallbackQuery):
    receipt_id = callback.data.split(":")[1]
    receipt = await ReceiptService.get_receipt(receipt_id)
    logger.info(f"{receipt=}")
    if not receipt:
        await callback.message.answer("Покупки не найдены.")
        return
    address = receipt.address.replace(",,", ",")
    lines = [
        f"🏪 {receipt.retail_place or 'Без названия'}\n📍 {address or 'Адрес не указан'}\n",
        "🧾 Покупки:",
    ]
    for item in receipt.items:
        lines.append(
            f"{item.name}\n{item.price / 100:.2f} ₽ × {item.quantity} = {item.sum / 100:.2f} ₽"
        )
    lines.append(f"\nИтого: {receipt.total_sum / 100:.2f} ₽")
    await callback.message.answer("\n".join(lines))
    await callback.answer()


@router.callback_query(F.data.startswith("delete:"))
async def delete_receipt(callback: CallbackQuery):
    receipt_id = callback.data.split(":")[1]
    await ReceiptService.delete_receipt(receipt_id)
    await callback.message.edit_text("✅ Чек удалён.")
    await callback.answer()


@router.callback_query(F.data.startswith("download:"))
async def download_receipt_handler(callback: CallbackQuery):
    receipt_id = callback.data.split(":")[1]

    # Получаем чек из БД
    receipt = await ReceiptService.get_receipt(receipt_id)
    if not receipt:
        await callback.answer("Чек не найден", show_alert=True)
        return
    qr_data = receipt.to_qr_string()
    redis_key = f"receipt_{receipt.receipt_id}"
    await async_redis_client.hset(
        redis_key,
        mapping={
            "telegram_id": callback.from_user.id,
            "qr_data": qr_data,
        },
    )
    download_receipt.delay(redis_key)
    await callback.message.answer("Загрузка начата. Требуется несколько секунд...")


def register_users_receipts_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
