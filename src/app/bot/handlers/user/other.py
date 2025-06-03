import logging
import os
import uuid
from typing import Dict

from aiogram import Router, F, Dispatcher, types
from app.tasks.image_check import process_check

from core import settings

logger = logging.getLogger(__name__)
router = Router()

IMAGE_FOLDER = settings.uploader.DIR

# Временное хранилище для ожидания категорий
user_states: Dict[int, str] = {}


@router.message(F.photo)
async def handle_photo(message: types.Message):
    # Создаем папку для изображений, если ее нет
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    # Генерируем уникальное имя файла
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(IMAGE_FOLDER, filename)

    # Сохраняем изображение
    await message.bot.download_file(file.file_path, filepath)

    # Запускаем задачу Celery
    task = process_check.delay(filepath)
    logger.info(f"Изображение сохранено. Обработка начата (ID задачи: {task.id})")

    # Запоминаем файл и просим категорию
    user_states[message.from_user.id] = filepath
    await message.answer("Введите название категории для этого чека:")


@router.message(F.text)
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
            category_id=category.id,
        )
        session.add(image)
        await session.commit()

    await message.answer(f"Изображение сохранено в категорию '{category_name}'")


def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
