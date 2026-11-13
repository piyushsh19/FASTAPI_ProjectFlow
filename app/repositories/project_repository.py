
from sqlalchemy import func, select
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


def get_projects(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 20,
):
    base_statement = select(Project).where(
        Project.owner_id == owner_id
    )

    total = db.scalar(
        select(func.count()).select_from(
            base_statement.subquery()
        )
    ) or 0

    statement = (
        base_statement
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    items = list(db.scalars(statement).all())

    return {
        "items": items,
        "total": total,
    }


def update_project(db: Session, project: Project, updates: dict):
    for key, value in updates.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
