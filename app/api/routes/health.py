
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.redis import redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    # Keep the existing endpoint for backward compatibility.
    return {
        "status": "healthy",
        "service": "projectflow-api",
    }


@router.get("/health/live", tags=["Health"])
def liveness_check():
    """Check whether the API process is running."""
    return {
        "status": "alive",
    }


@router.get("/health/db", tags=["Health"])
def database_health(db: Session = Depends(get_db)):
    # Keep the existing database health endpoint.
    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }


@router.get("/health/ready", tags=["Health"])
async def readiness_check(db: Session = Depends(get_db)):
    """Check whether the API can communicate with its dependencies."""

    checks = {
        "database": "ok",
        "redis": "ok",
    }

    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Database readiness check failed")
        checks["database"] = "unavailable"

    try:
        await redis_client.ping()
    except RedisError:
        logger.exception("Redis readiness check failed")
        checks["redis"] = "unavailable"

    if any(value != "ok" for value in checks.values()):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "checks": checks,
    }
