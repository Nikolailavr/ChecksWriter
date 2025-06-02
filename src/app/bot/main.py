import logging
import os
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Папка для сохранения файлов
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def parse_image(file_path: str) -> str:
    # Здесь вызывай свой парсер и передавай путь к файлу
    # Для примера просто возвращаем путь
    # Вместо этого вставь реальный вызов парсера и обработку
    return f"Парсер получил файл: {file_path}"


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Берём самое большое фото из размеров
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path

    # Локальный путь для сохранения
    local_file_path = os.path.join(DOWNLOAD_DIR, f"{photo.file_id}.jpg")

    # Скачиваем файл
    await bot.download_file(file_path, local_file_path)
    await message.reply(f"Фото сохранено: {local_file_path}")

    # Вызываем парсер и получаем результат
    result = await parse_image(local_file_path)

    # Отправляем результат пользователю
    await message.answer(result)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
