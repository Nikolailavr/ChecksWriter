import logging
from aiogram import Router, F, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

from core import settings

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.photo)
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
            category_id=category.id,
        )
        session.add(image)
        await session.commit()

    await message.answer(f"Изображение сохранено в категорию '{category_name}'")

def register_users_other_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)