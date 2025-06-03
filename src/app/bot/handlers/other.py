import logging
from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import StateFilter

from core import settings


logger = logging.getLogger(__name__)
router = Router()


def register_other_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков"""
    dp.include_router(router)
