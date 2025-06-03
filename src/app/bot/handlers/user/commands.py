import logging
from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from core import settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def __start(msg: Message) -> None:
    await msg.answer(
        "Привет! Отправь мне изображение, и я сохраню его в указанной категории.\n"
        "Доступные команды:\n"
        "/categories - Показать все категории\n"
        "/images <категория> - Показать изображения в категории"
    )


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
