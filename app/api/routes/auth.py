from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.rate_limiter import rate_limit
from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            rate_limit(
                limit=5,
                window_seconds=60,
                scope="auth:register",
            )
        )
    ],
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return auth_service.register_user(
        db,
        user.model_dump(),
    )


@router.post(
    "/login",
    dependencies=[
        Depends(
            rate_limit(
                limit=5,
                window_seconds=60,
                scope="auth:login",
            )
        )
    ],
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return auth_service.login_user(
        db,
        email=form_data.username,
        password=form_data.password,
    )