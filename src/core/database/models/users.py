from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from core.database.models.base import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False
    )
    phone: Mapped[int] = mapped_column(Integer, nullable=True)
