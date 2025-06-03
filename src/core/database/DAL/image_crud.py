from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from core.database.models import Image
from core.database.schemas import (ImageCreate, ImageUpdate, ImageStatus,)


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

    async def get(
        self,
        filename: str = None,
        user_id: int = None,
    ) -> Optional[Image] | list[Image] | None:
        if filename:
            result = await self.session.execute(
                select(Image).where(Image.filename == filename)
            )
            return result.scalar_one_or_none()
        elif user_id:
            result = await self.session.execute(
                select(Image).where(Image.user_id == user_id)
            )
            return result.scalars().all()
        return None


    async def update(self, filename: str, update_data: ImageUpdate) -> Optional[Image]:
        """Обновление данных изображения"""
        try:
            await self.session.execute(
                update(Image)
                .where(Image.filename == filename)
                .values(
                    category=update_data.category,
                    processing_status=update_data.processing_status,
                    result_data=update_data.result_data,
                    updated_at=datetime.now(),
                )
            )
            await self.session.commit()
            return await self.get(filename=filename)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete(self, filename: str) -> bool:
        """Удаление изображения"""
        try:
            await self.session.execute(delete(Image).where(Image.filename == filename))
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def update_status(
        self, filename: str, status: ImageStatus, result_data: Optional[str] = None
    ) -> Optional[Image]:
        """Обновление статуса обработки изображения"""
        try:
            await self.session.execute(
                update(Image)
                .where(Image.filename == filename)
                .values(
                    processing_status=status,
                    result_data=result_data,
                    updated_at=datetime.now(),
                )
            )
            await self.session.commit()
            return await self.get(filename=filename)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_by_task_id(self, task_id: str) -> Optional[Image]:
        """Получение изображения по ID задачи Celery"""
        result = await self.session.execute(
            select(Image).where(Image.celery_task_id == task_id)
        )
        return result.scalar_one_or_none()
