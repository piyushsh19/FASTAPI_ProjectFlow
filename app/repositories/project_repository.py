
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
    sort_by: str = "created_at",
    order: str = "desc",
):
    sort_columns = {
        "created_at": Project.created_at,
        "updated_at": Project.updated_at,
        "name": Project.name,
    }

    sort_column = sort_columns.get(sort_by)

    if sort_column is None:
        raise ValueError(f"Unsupported project sort field: {sort_by}")

    if order == "asc":
        sort_expression = sort_column.asc()
    else:
        sort_expression = sort_column.desc()

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
        .order_by(sort_expression, Project.id.asc())
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
