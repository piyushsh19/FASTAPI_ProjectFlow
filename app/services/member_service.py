
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Project, ProjectMember
from app.repositories import member_repository
from app.services.project_access import get_project_and_role


def get_project_for_manager(
    db: Session,
    project_id: int,
    actor_id: int,
) -> tuple[Project, str]:
    """
    Allow project owners and admins to manage project members.
    """
    project, actor_role = get_project_and_role(
        db,
        project_id,
        actor_id,
    )

    if actor_role not in {"owner", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner or an admin can manage members",
        )

    return project, actor_role


def add_project_member(
    db: Session,
    project_id: int,
    owner_id: int,
    email: str,
    role: str,
):
    project, actor_role = get_project_for_manager(
        db,
        project_id,
        owner_id,
    )

    # Only the project owner can grant admin privileges.
    if actor_role == "admin" and role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can assign the admin role",
        )

    user = member_repository.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist",
        )

    if user.id == project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project owner cannot be added as a member",
        )

    existing_member = member_repository.get_membership(
        db,
        project_id,
        user.id,
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a project member",
        )

    return member_repository.create_member(
        db,
        project_id,
        user.id,
        role,
    )


def list_project_members(
    db: Session,
    project_id: int,
    user_id: int,
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    is_owner = project.owner_id == user_id

    if not is_owner:
        membership = member_repository.get_membership(
            db,
            project_id,
            user_id,
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

    return member_repository.get_project_members(db, project_id)


def update_project_member_role(
    db: Session,
    project_id: int,
    owner_id: int,
    user_id: int,
    role: str,
):
    project, actor_role = get_project_for_manager(
        db,
        project_id,
        owner_id,
    )

    if user_id == project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project owner's role cannot be changed",
        )

    member = member_repository.get_membership(
        db,
        project_id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    # Admins cannot modify their own role or another admin's role.
    if actor_role == "admin":
        if user_id == owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot change their own role",
            )

        if member.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot modify another admin's role",
            )

        if role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can assign the admin role",
            )

    return member_repository.update_member_role(
        db,
        member,
        role,
    )


def remove_project_member(
    db: Session,
    project_id: int,
    owner_id: int,
    user_id: int,
) -> None:
    project, actor_role = get_project_for_manager(
        db,
        project_id,
        owner_id,
    )

    if user_id == project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project owner cannot be removed",
        )

    member = member_repository.get_membership(
        db,
        project_id,
        user_id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    # Admins cannot remove themselves or another admin.
    if actor_role == "admin":
        if user_id == owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot remove themselves",
            )

        if member.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot remove another admin",
            )

    member_repository.delete_member(db, member)
