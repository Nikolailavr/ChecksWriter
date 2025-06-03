from pydantic import BaseModel, Field
from typing import Optional

from pydantic_extra_types.epoch import Integer


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    telegram_id: int = Field(Integer, description="ID пользователя в Telegram")
    phone: Optional[int] = Field(None, description="Номер телефона")
