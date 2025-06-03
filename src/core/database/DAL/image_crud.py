from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from core.database.models import Image
from core.database.schemas import ImageCreate, ImageUpdate, ImageStatus


class ImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, image_data: ImageCreate) -> Image:
        """Создание нового изображения"""
        try:
            image = Image(
                filename=image_data.filename,
                user_id=image_data.user_id,
                category=image_data.category,
            )
            self.session.add(image)
            await self.session.commit()
            await self.session.refresh(image)
            return image
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_by_id(self, image_id: int) -> Optional[Image]:
        """Получение изображения по ID"""
        result = await self.session.execute(select(Image).where(Image.id == image_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[Image]:
        """Получение всех изображений пользователя"""
        result = await self.session.execute(
            select(Image).where(Image.user_id == user_id)
        )
        return result.scalars().all()

    async def update(self, image_id: int, update_data: ImageUpdate) -> Optional[Image]:
        """Обновление данных изображения"""
        try:
            await self.session.execute(
                update(Image)
                .where(Image.id == image_id)
                .values(
                    category=update_data.category,
                    processing_status=update_data.processing_status,
                    result_data=update_data.result_data,
                    updated_at=datetime.now(),
                )
            )
            await self.session.commit()
            return await self.get_by_id(image_id)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete(self, image_id: int) -> bool:
        """Удаление изображения"""
        try:
            await self.session.execute(delete(Image).where(Image.id == image_id))
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def update_status(
        self, image_id: int, status: ImageStatus, result_data: Optional[str] = None
    ) -> Optional[Image]:
        """Обновление статуса обработки изображения"""
        try:
            await self.session.execute(
                update(Image)
                .where(Image.id == image_id)
                .values(
                    processing_status=status,
                    result_data=result_data,
                    updated_at=datetime.now(),
                )
            )
            await self.session.commit()
            return await self.get_by_id(image_id)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_by_task_id(self, task_id: str) -> Optional[Image]:
        """Получение изображения по ID задачи Celery"""
        result = await self.session.execute(
            select(Image).where(Image.celery_task_id == task_id)
        )
        return result.scalar_one_or_none()
