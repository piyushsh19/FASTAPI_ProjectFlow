from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings
from app.api.routes.projects import router as projects_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
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