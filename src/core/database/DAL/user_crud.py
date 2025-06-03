from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from core.database.models import User
from core.database.schemas import UserBase


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserBase) -> User:
        """Создание нового пользователя"""
        try:
            user = User(**user.model_dump())
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get(self, user: UserBase) -> User | None:
        """Получение пользователя по telegram_id"""
        if user.phone is not None:
            stmt = select(User).where(User.phone == user.phone)
        else:
            stmt = select(User).where(User.telegram_id == user.telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_phone(self, telegram_id: int, new_phone: int) -> User | None:
        """Обновление номера телефона пользователя"""
        try:
            await self.session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(phone=new_phone)
            )
            await self.session.commit()
            return await self.get(telegram_id)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete(self, telegram_id: int) -> bool:
        """Удаление пользователя"""
        try:
            await self.session.execute(
                delete(User).where(User.telegram_id == telegram_id)
            )
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
