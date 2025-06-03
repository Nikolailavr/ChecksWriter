from datetime import datetime

from sqlalchemy import (
    String,
    PickleType,
    DateTime,
    Text,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models import Base


class CeleryTaskResult(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[object] = mapped_column(PickleType)
    date_done: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    traceback: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(255))
    args: Mapped[str] = mapped_column(Text)
    kwargs: Mapped[str] = mapped_column(Text)
    worker: Mapped[str] = mapped_column(String(100))
    retries: Mapped[int] = mapped_column(Integer)
    queue: Mapped[str] = mapped_column(String(100))


class CeleryGroupResult(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    result: Mapped[object] = mapped_column(PickleType)
    date_done: Mapped[datetime] = mapped_column(DateTime, nullable=False)
