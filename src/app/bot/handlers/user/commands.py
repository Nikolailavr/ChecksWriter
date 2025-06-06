import logging
from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from app.bot.keyboards.user import show_categories
from core.services.receipts import ReceiptService
from core.services.users import UserService

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def __start(msg: Message) -> None:
    await UserService.get_or_create(telegram_id=msg.from_user.id)
    await msg.answer(
        "Привет! Отправь мне фото QR чека, и я сохраню его в указанной категории.\n"
        "Доступные команды:\n"
        "/list - Показать все категории"
    )


@router.message(Command("list"))
async def list_categories(msg: Message):
    categories = await ReceiptService.get_categories(msg.from_user.id)
    if not categories:
        await msg.answer("Нет категорий")
        return
    await show_categories(msg, categories, page=0, edit=False)


def register_users_commands_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
