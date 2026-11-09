
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify Redis is available when the application starts.
    await redis_client.ping()

    yield

    # Stop project subscribers before closing Redis.
    await manager.shutdown()

    # Close the Redis connection pool.
    await redis_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
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
