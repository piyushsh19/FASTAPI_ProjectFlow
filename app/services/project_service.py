
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, Project
from app.repositories import project_repository
from app.services.project_access import (
    get_project_and_role,
    require_project_role,
)


def create_project(db: Session, project_data: dict) -> Project:
    owner = db.get(User, project_data["owner_id"])

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project owner not found",
        )

    return project_repository.create_project(db, project_data)


def get_project(
    db: Session,
    project_id: int,
    user_id: int,
) -> Project:
    project, _ = get_project_and_role(
        db,
        project_id,
        user_id,
    )
    return project


def get_projects(
    db: Session,
    skip: int,
    limit: int,
    user_id: int,
    sort_by: str = "created_at",
    order: str = "desc",
):
    return project_repository.get_projects(
        db=db,
        owner_id=user_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )


def update_project(
    db: Session,
    project_id: int,
    updates: dict,
    user_id: int,
):
    project = require_project_role(
        db,
        project_id,
        user_id,
        {"owner", "admin"},
    )

    return project_repository.update_project(
        db,
        project,
        updates,
    )


def delete_project(
    db: Session,
    project_id: int,
    user_id: int,
):
    project, role = get_project_and_role(
        db,
        project_id,
        user_id,
    )

    if role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete the project",
        )

    project_repository.delete_project(db, project)
