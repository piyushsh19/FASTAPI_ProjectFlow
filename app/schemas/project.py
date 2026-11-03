from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ProjectStatus = Literal["active", "completed", "archived"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str | None = None
    owner_id: int = Field(gt=0)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    status: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)