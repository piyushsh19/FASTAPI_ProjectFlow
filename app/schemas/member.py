from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


MemberRole = Literal["admin", "member", "viewer"]


class ProjectMemberCreate(BaseModel):
    email: EmailStr
    role: MemberRole = "member"


class ProjectMemberRoleUpdate(BaseModel):
    role: MemberRole


class MemberUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: MemberRole
    created_at: datetime
    user: MemberUserResponse

    model_config = ConfigDict(from_attributes=True)