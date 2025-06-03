from aiogram import Dispatcher

from app.bot.handlers.other import register_other_handlers
from app.bot.handlers.user import register_users_handlers
from app.bot.handlers.user import register_users_other_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_users_handlers,
        register_users_other_handlers,
        register_other_handlers,
    )
    for handler in handlers:
        handler(dp)
