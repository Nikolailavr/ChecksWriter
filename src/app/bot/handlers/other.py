import os
import uuid
from pathlib import Path
from typing import Dict

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from sqlalchemy import select

from database import Session, Image, Category
from config import Config

bot = Bot(token=Config.TOKEN)
dp = Dispatcher()

# Временное хранилище для ожидания категорий
user_states: Dict[int, str] = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Отправь мне изображение, и я сохраню его в указанной категории.\n"
        "Доступные команды:\n"
        "/categories - Показать все категории\n"
        "/images <категория> - Показать изображения в категории"
    )

@dp.message(Command("categories"))
async def list_categories(message: types.Message):
    async with Session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()

    if not categories:
        await message.answer("Категории пока не добавлены")
        return

    text = "Доступные категории:\n" + "\n".join([cat.name for cat in categories])
    await message.answer(text)

@dp.message(Command("images"))
async def list_images(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите категорию: /images <категория>")
        return

    category_name = args[1]
    async with Session() as session:
        category = await session.scalar(
            select(Category).where(Category.name == category_name)
        )

        if not category:
            await message.answer(f"Категория '{category_name}' не найдена")
            return

        images = await session.scalars(
            select(Image).where(Image.category_id == category.id)
        )

        if not images:
            await message.answer(f"В категории '{category_name}' нет изображений")
            return

        for image in images:
            photo = FSInputFile(image.filepath)
            await message.answer_photo(photo, caption=f"Категория: {category_name}")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    # Создаем папку для изображений, если ее нет
    os.makedirs("images", exist_ok=True)

    # Генерируем уникальное имя файла
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join("images", filename)

    # Сохраняем изображение
    await bot.download_file(file.file_path, filepath)

    # Запоминаем файл и просим категорию
    user_states[message.from_user.id] = filepath
    await message.answer("Введите название категории для этого изображения:")

@dp.message(F.text)
async def handle_category(message: types.Message):
    if message.from_user.id not in user_states:
        return

    filepath = user_states.pop(message.from_user.id)
    category_name = message.text.strip()

    async with Session() as session:
        # Находим или создаем категорию
        category = await session.scalar(
            select(Category).where(Category.name == category_name)
        )

        if not category:
            category = Category(name=category_name)
            session.add(category)
            await session.commit()
            await session.refresh(category)

        # Сохраняем изображение в БД
        image = Image(
            filename=os.path.basename(filepath),
            filepath=filepath,
            category_id=category.id
        )
        session.add(image)
        await session.commit()

    await message.answer(f"Изображение сохранено в категорию '{category_name}'")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())