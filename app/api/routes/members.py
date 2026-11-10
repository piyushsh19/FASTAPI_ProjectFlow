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
from fastapi import BackgroundTasks
from app.models.project import Project
from app.services.notification_dispatcher import dispatch_notification



router = APIRouter(tags=["Project Members"])



@router.post(
    "/projects/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id: int,
    member: ProjectMemberCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Existing membership business logic and authorization.
    member_record = member_service.add_project_member(
        db=db,
        project_id=project_id,
        owner_id=current_user.id,
        email=str(member.email),
        role=member.role,
    )

    # Get project information for the notification.
    project = db.get(Project, project_id)

    # Notify the newly added member.
    dispatch_notification(
        db,
        background_tasks,
        user_id=member_record.user_id,
        notification_type="member_added",
        title="Added to a project",
        message=f"You have been added to project: {project.name}",
        data={
            "project_id": project_id,
        },
    )

    return member_record

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