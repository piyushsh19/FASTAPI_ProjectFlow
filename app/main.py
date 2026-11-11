
# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.members import router as members_router
from app.api.routes.websockets import router as websockets_router

from app.core.config import settings
from app.db.redis import redis_client
from app.services.websocket_manager import manager
from app.api.routes import notifications
from app.api.routes import notification_websockets
import logging

from app.services.notification_websocket_manager import (
    notification_manager,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis availability is reported by /health/ready.
    # Do not prevent the API from starting if Redis is unavailable.
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception:
        logger.exception(
            "Redis is unavailable during application startup"
        )

    yield

    # Stop both WebSocket managers before closing Redis.
    await manager.shutdown()
    await notification_manager.shutdown()

    await redis_client.aclose()

    logger.info("Application shutdown completed")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to ProjectFlow API",
        "version": settings.app_version,
    }


app.include_router(health_router)
app.include_router(projects_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(members_router)
app.include_router(websockets_router)
app.include_router(notifications.router)
app.include_router(notification_websockets.router)
