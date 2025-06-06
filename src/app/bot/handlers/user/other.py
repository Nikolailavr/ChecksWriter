import logging

from aiogram import Router, Dispatcher

logger = logging.getLogger(__name__)
router = Router()



def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
