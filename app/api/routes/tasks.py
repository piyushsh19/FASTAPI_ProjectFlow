
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskResponse,
)
from app.services import task_service


router = APIRouter(
    tags=["Tasks"],
)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return task_service.create_task(
        db,
        project_id,
        current_user.id,
        task.model_dump(),
    )


@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[TaskResponse],
)
def get_project_tasks(
    project_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    task_status: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    assigned_to: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return task_service.get_project_tasks(
        db,
        project_id,
        current_user.id,
        skip=skip,
        limit=limit,
        task_status=task_status,
        priority=priority,
        assigned_to=assigned_to,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return task_service.get_task(
        db,
        task_id,
        current_user.id,
    )


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return task_service.update_task(
        db,
        task_id,
        current_user.id,
        updates.model_dump(exclude_unset=True),
    )


@router.patch(
    "/tasks/{task_id}/status",
    response_model=TaskResponse,
)
def update_task_status(
    task_id: int,
    updates: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return task_service.update_task_status(
        db,
        task_id,
        current_user.id,
        updates.status,
    )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    task_service.delete_task(
        db,
        task_id,
        current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
