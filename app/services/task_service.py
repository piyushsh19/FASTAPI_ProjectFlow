
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Project, ProjectMember, Task
from app.repositories import task_repository
from app.services.project_access import get_project_and_role


def check_project_access(
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


def check_project_write_access(
    db: Session,
    project_id: int,
    user_id: int,
) -> Project:
    project, role = get_project_and_role(
        db,
        project_id,
        user_id,
    )

    if role not in {"owner", "admin", "member"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify project tasks",
        )

    return project


def check_task_access(
    db: Session,
    task_id: int,
    user_id: int,
) -> Task:
    task = task_repository.get_task(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    check_project_access(
        db,
        task.project_id,
        user_id,
    )

    return task


def validate_assignee(
    db: Session,
    project_id: int,
    assigned_to: int | None,
) -> None:
    if assigned_to is None:
        return

    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if assigned_to == project.owner_id:
        return

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == assigned_to,
    ).first()

    if membership is None or membership.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Assignee must be an owner, admin, or member "
                "of the project"
            ),
        )


def create_task(
    db: Session,
    project_id: int,
    user_id: int,
    task_data: dict,
):
    check_project_write_access(db, project_id, user_id)

    validate_assignee(
        db,
        project_id,
        task_data.get("assigned_to"),
    )

    task_data["project_id"] = project_id

    return task_repository.create_task(
        db,
        task_data,
    )


def get_project_tasks(
    db: Session,
    project_id: int,
    user_id: int,
    **filters,
):
    check_project_access(
        db,
        project_id,
        user_id,
    )

    return task_repository.get_project_tasks(
        db,
        project_id,
        **filters,
    )


def get_task(
    db: Session,
    task_id: int,
    user_id: int,
):
    return check_task_access(
        db,
        task_id,
        user_id,
    )


def update_task(
    db: Session,
    task_id: int,
    user_id: int,
    updates: dict,
):
    task = check_task_access(
        db,
        task_id,
        user_id,
    )

    check_project_write_access(
        db,
        task.project_id,
        user_id,
    )

    if "assigned_to" in updates:
        validate_assignee(
            db,
            task.project_id,
            updates["assigned_to"],
        )

    return task_repository.update_task(
        db,
        task,
        updates,
    )


def update_task_status(
    db: Session,
    task_id: int,
    user_id: int,
    new_status: str,
):
    task = check_task_access(
        db,
        task_id,
        user_id,
    )

    check_project_write_access(
        db,
        task.project_id,
        user_id,
    )

    return task_repository.update_task(
        db,
        task,
        {"status": new_status},
    )


def delete_task(
    db: Session,
    task_id: int,
    user_id: int,
):
    task = check_task_access(
        db,
        task_id,
        user_id,
    )

    _, role = get_project_and_role(
        db,
        task.project_id,
        user_id,
    )

    if role not in {"owner", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners and admins can delete tasks",
        )

    task_repository.delete_task(
        db,
        task,
    )
