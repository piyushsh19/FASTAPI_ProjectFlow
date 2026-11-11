
import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def get_error_code(status_code: int) -> str:
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }

    return error_codes.get(status_code, "HTTP_ERROR")


async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
        },
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    # Preserve existing HTTPException status codes and messages.
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": get_error_code(exc.status_code),
                "message": str(exc.detail),
            },
        },
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors,
            },
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )
