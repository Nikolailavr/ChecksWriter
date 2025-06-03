import logging
from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import StateFilter

from core import settings


logger = logging.getLogger(__name__)
router = Router()


@router.message(StateFilter(None))
async def other_messages(msg: Message, bot: Bot) -> None:
    """
    Обработка всех текстовых сообщений
    """
    user = await UserService.get_or_create_user(telegram_id=msg.from_user.id)
    match user.last_command:
        case "/add":
            await handle_add_link(msg, bot)
            await UserService.update_last_command(
                telegram_id=msg.from_user.id,
                command="",
            )
        case "/delete":
            await handle_delete_link(msg, bot)
            await UserService.update_last_command(
                telegram_id=msg.from_user.id,
                command="",
            )
        case _:
            await msg.answer(settings.msg.BAD_MSG)
            await UserService.update_last_command(
                telegram_id=msg.from_user.id,
                command="",
            )


async def handle_add_link(msg: Message, bot: Bot) -> None:
    """
    Обработка добавления ссылки
    """
    if msg.text.startswith("https://www.ozon.ru/product/"):
        url = msg.text.rstrip("/")  # Удаляем trailing slash
        subscribe = SubscribeBase(telegram_id=msg.from_user.id, url=url)
        try:
            await SubscribeService.add(subscribe)
            from parser import Parser

            await Parser().check(subscribe.url)
            await bot.delete_message(
                chat_id=msg.from_user.id, message_id=msg.message_id
            )
            await msg.answer(settings.msg.GOOD_URL)
        except Exception as ex:
            logger.error(f"Error adding link: {ex}")
            await msg.answer(settings.msg.BAD_URL)
    else:
        await msg.answer(settings.msg.BAD_URL)


async def handle_delete_link(msg: Message, bot: Bot) -> None:
    """
    Обработка удаления ссылки
    """
    try:
        await SubscribeService.delete(
            subscribe=SubscribeBase(
                telegram_id=msg.from_user.id,
                url=msg.text,
            )
        )
        await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)
        await msg.answer(settings.msg.GOOD_DELETE)
    except Exception as ex:
        logger.error(f"Error deleting link: {ex}")
        await msg.answer("Произошла ошибка при удалении ссылки")


def register_other_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков"""
    dp.include_router(router)