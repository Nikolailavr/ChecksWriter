import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from app.bot.handlers import register_all_handlers
from core import settings

logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram.token)
dp = Dispatcher(storage=MemoryStorage())


async def send_msg(
    chat_id: int,
    text: str,
    message_id: int = None,
):
    await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

async def send_image(chat_id: int, image_path: str):
    photo = FSInputFile(image_path)
    await bot.send_photo(chat_id, photo)

async def start_bot():
    # Создаем папку для изображений, если ее нет
    os.makedirs(settings.uploader.DIR, exist_ok=True)
    # Регистрация обработчиков
    register_all_handlers(dp)

    # Запуск поллинга
    await dp.start_polling(bot, skip_updates=True)
