from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base
from enum import Enum

if TYPE_CHECKING:
    from .users import User


class Image(Base):

    class Status(Enum):
        PENDING = "pending"
        PROCESSING = "processing"
        DONE = "done"
        FAILED = "failed"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    celery_task_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    processing_status: Mapped[Status] = mapped_column(default=Status.PENDING)
    result_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.now, nullable=True
    )
    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="images")

    category: Mapped[str] = mapped_column(String, nullable=True)
