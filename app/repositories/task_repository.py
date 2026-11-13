
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task


def create_task(db: Session, task_data: dict) -> Task:
    task = Task(**task_data)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)



def get_project_tasks(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 20,
    task_status: str | None = None,
    priority: str | None = None,
    assigned_to: int | None = None,
):
    # Base query: tasks belonging to the requested project.
    base_statement = select(Task).where(
        Task.project_id == project_id
    )

    # Apply filters before counting.
    if task_status:
        base_statement = base_statement.where(
            Task.status == task_status
        )

    if priority:
        base_statement = base_statement.where(
            Task.priority == priority
        )

    if assigned_to is not None:
        base_statement = base_statement.where(
            Task.assigned_to == assigned_to
        )

    # Count all matching tasks before pagination.
    total = db.scalar(
        select(func.count()).select_from(base_statement.subquery())
    ) or 0

    # Fetch the requested page.
    statement = (
        base_statement
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    items = list(db.scalars(statement).all())

    return {
        "items": items,
        "total": total,
    }


def update_task(
    db: Session,
    task: Task,
    updates: dict,
) -> Task:

    for key, value in updates.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
