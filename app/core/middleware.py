import logging
import time
import uuid

from fastapi import Request

from app.core.request_context import request_id_context

logger = logging.getLogger("app.http")


async def request_id_middleware(request: Request, call_next):
    """
    Assign a unique request ID and propagate it through
    the current request's logging context.
    """

    incoming_request_id = request.headers.get("X-Request-ID")

    try:
        request_id = str(uuid.UUID(incoming_request_id))
    except (ValueError, TypeError, AttributeError):
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id
    token = request_id_context.set(request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    finally:
        request_id_context.reset(token)


async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "HTTP request | method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.exception(
            "HTTP request failed | method=%s path=%s duration_ms=%s",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise