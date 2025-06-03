import logging
from aiogram import Router, F, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from core import settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def __start(msg: Message) -> None:
    text = f"Привет, <b>{msg.from_user.first_name}</b>!\n{settings.msg.HELP_MESSAGE}"
    await msg.answer(text)
    await UserService.get_or_create_user(telegram_id=msg.from_user.id)



def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)