from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.services import project_service
from app.schemas.pagination import PaginatedResponse

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_data = project.model_dump()
    project_data["owner_id"] = current_user.id

    return project_service.create_project(db, project_data)



@router.get("/", response_model=PaginatedResponse[ProjectResponse])
def get_projects(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = project_service.get_projects(
        db,
        skip,
        limit,
        current_user.id,
    )

    return {
        "items": result["items"],
        "total": result["total"],
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(result["items"]) < result["total"],
    }


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.get_project(
        db,
        project_id,
        current_user.id,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    updates: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.update_project(
        db,
        project_id,
        updates.model_dump(exclude_unset=True),
        current_user.id,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.delete_project(
        db,
        project_id,
        current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)