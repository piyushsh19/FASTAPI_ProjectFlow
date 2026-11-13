
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    type: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1)
    data: dict[str, Any] | None = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_read: bool
    created_at: datetime



class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
    skip: int = Field(ge=0)
    limit: int = Field(gt=0)
    has_more: bool



class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationReadResponse(BaseModel):
    id: int
    is_read: bool
