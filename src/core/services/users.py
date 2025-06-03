from core.database.DAL import UserRepository
from core.database.db_helper import db_helper
from core.database.models import User
from core.database.schemas import UserBase


class UserService:
    @staticmethod
    async def get_or_create(telegram_id: int, phone: int = None) -> User:
        async with db_helper.get_session() as session:
            user_base = UserBase(
                telegram_id=telegram_id,
                phone=phone,
            )
            user = await UserRepository(session).get(user_base)
            if user is None:
                user = await UserRepository(session).create(user_base)
            return user
