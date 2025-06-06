from aiogram import Dispatcher

from app.bot.handlers.other import register_other_handlers
from app.bot.handlers.user import (
    register_users_commands_handlers,
    register_users_photos_handlers,
    register_users_receipts_handlers,
    register_users_categories_handlers,
    register_users_other_handlers,
)


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_users_commands_handlers,
        register_users_receipts_handlers,
        register_users_categories_handlers,
        register_users_other_handlers,
        register_users_photos_handlers,
        register_other_handlers,
    )
    for handler in handlers:
        handler(dp)
