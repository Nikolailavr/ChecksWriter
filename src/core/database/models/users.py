from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.models.base import Base

if TYPE_CHECKING:
    from .receipts import Receipt


class User(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False
    )
    phone: Mapped[int] = mapped_column(Integer, nullable=True)

    # Связь с чеками
    receipts: Mapped[list["Receipt"]] = relationship(back_populates="user_rel")
