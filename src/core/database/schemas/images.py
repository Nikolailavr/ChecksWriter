from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ImageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ImageBase(BaseModel):
    filename: str = Field(..., max_length=255)
    user_id: int = Field(..., description="Telegram user ID")
    category: Optional[str] = Field(None, max_length=100)


class ImageCreate(ImageBase):
    pass


class ImageUpdate(BaseModel):
    category: Optional[str] = Field(None, max_length=100)
    processing_status: Optional[ImageStatus] = None
    result_data: Optional[str] = None


class ImageInDB(ImageBase):
    id: int
    celery_task_id: Optional[str] = None
    processing_status: ImageStatus = ImageStatus.PENDING
    result_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ImageResponse(ImageInDB):
    pass
