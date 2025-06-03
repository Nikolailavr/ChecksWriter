from core.database import db_helper
from core.database.DAL.image_crud import ImageRepository
from core.database.models import Image
from core.database.schemas import ImageCreate


class ImageService:

    @staticmethod
    async def get_or_create(telegram_id: int, filename: str) -> Image:
        async with db_helper.get_session() as session:
            image = await ImageRepository(session).get(filename)
            if image is None:
                image_base = ImageCreate(
                    filename=filename,
                    user_id=telegram_id,
                    category=None,
                )
                image = await ImageRepository(session).create(image_base)
            return image

    @staticmethod
    async def delete(filename: str):
        async with db_helper.get_session() as session:
            await ImageRepository(session).delete(filename)
