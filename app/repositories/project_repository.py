from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project


def create_project(db: Session, project_data: dict) -> Project:
    project = Project(**project_data)

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_projects(db: Session, skip: int = 0, limit: int = 20):
    statement = (
        select(Project)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()


def update_project(db: Session, project: Project, updates: dict):
    for key, value in updates.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()