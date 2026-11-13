
# app/main.py

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging_config import setup_logging

# Configure logging before creating application loggers.
setup_logging(
    debug=settings.debug,
    log_level=settings.log_level,
)

logger = logging.getLogger(__name__)

# API routes
from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.members import router as members_router
from app.api.routes.websockets import router as websockets_router
from app.api.routes import notifications
from app.api.routes import notification_websockets

# Exception handling
from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

# Middleware
from app.core.middleware import (
    request_id_middleware,
    request_logging_middleware,
)
from app.core.security_middleware import (
    security_headers_middleware,
)

# Infrastructure
from app.db.redis import redis_client
from app.services.websocket_manager import manager
from app.services.notification_websocket_manager import (
    notification_manager,
)


# --------------------------------------------------
# Application Lifespan
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

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


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.state.environment = settings.environment.lower()


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ],
    expose_headers=[
        "X-Request-ID",
    ],
)


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

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


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to ProjectFlow API",
        "version": settings.app_version,
    }


# --------------------------------------------------
# Middleware Registration
# --------------------------------------------------

# Registration order is intentional.
# Request ID middleware wraps the other HTTP middleware
# so the request context is available during request logging.

app.middleware("http")(request_logging_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_id_middleware)


# --------------------------------------------------
# API Router Registration
# --------------------------------------------------

app.include_router(health_router)
app.include_router(projects_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(members_router)
app.include_router(websockets_router)
app.include_router(notifications.router)
app.include_router(notification_websockets.router)
