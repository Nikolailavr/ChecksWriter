import logging
from aiogram import Router, Dispatcher


logger = logging.getLogger(__name__)
router = Router()


def register_other_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков"""
    dp.include_router(router)
