from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.schemas.member import (
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberRoleUpdate,
)
from app.services import member_service


router = APIRouter(tags=["Project Members"])


@router.post(
    "/projects/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id: int,
    member: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return member_service.add_project_member(
        db=db,
        project_id=project_id,
        owner_id=current_user.id,
        email=str(member.email),
        role=member.role,
    )


@router.get(
    "/projects/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return member_service.list_project_members(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )


@router.patch(
    "/projects/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_project_member_role(
    project_id: int,
    user_id: int,
    updates: ProjectMemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return member_service.update_project_member_role(
        db=db,
        project_id=project_id,
        owner_id=current_user.id,
        user_id=user_id,
        role=updates.role,
    )


@router.delete(
    "/projects/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member_service.remove_project_member(
        db=db,
        project_id=project_id,
        owner_id=current_user.id,
        user_id=user_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)