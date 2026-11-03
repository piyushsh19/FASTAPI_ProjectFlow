from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, Project
from app.repositories import project_repository


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
    project = project_repository.get_project(db, project_id)

    if not project or project.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


def get_projects(
    db: Session,
    skip: int,
    limit: int,
    user_id: int,
):
    return project_repository.get_projects(
        db,
        owner_id=user_id,
        skip=skip,
        limit=limit,
    )


def update_project(
    db: Session,
    project_id: int,
    updates: dict,
    user_id: int,
):
    project = get_project(db, project_id, user_id)

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
    project = get_project(db, project_id, user_id)

    project_repository.delete_project(db, project)