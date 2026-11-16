
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Project, ProjectMember


def get_project_and_role(
    db: Session,
    project_id: int,
    user_id: int,
) -> tuple[Project, str]:
    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id == user_id:
        return project, "owner"

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project, membership.role


def require_project_role(
    db: Session,
    project_id: int,
    user_id: int,
    allowed_roles: set[str],
) -> Project:
    project, role = get_project_and_role(
        db,
        project_id,
        user_id,
    )

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    return project
