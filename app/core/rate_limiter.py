import logging
from typing import Callable

from fastapi import HTTPException, Request, status

from app.db.redis import redis_client

logger = logging.getLogger(__name__)

RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])

if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

local ttl = redis.call("TTL", KEYS[1])

return {current, ttl}
"""


def rate_limit(
    limit: int,
    window_seconds: int,
    scope: str,
) -> Callable:
    """
    Create a Redis-backed rate-limiting dependency.

    Args:
        limit: Maximum number of requests.
        window_seconds: Duration of the rate-limit window.
        scope: Unique identifier for the endpoint.
    """

    async def limiter(request: Request) -> None:
        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        redis_key = f"rate_limit:{scope}:{client_ip}"

        try:
            result = await redis_client.eval(
                RATE_LIMIT_SCRIPT,
                1,
                redis_key,
                window_seconds,
            )

            request_count = int(result[0])
            remaining_ttl = max(int(result[1]), 1)

        except Exception:
            logger.exception(
                "Rate limiter Redis operation failed | scope=%s",
                scope,
            )

            # Fail closed: do not allow unlimited requests if
            # the rate-limiting service is unavailable.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiting service temporarily unavailable",
            )

        if request_count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={
                    "Retry-After": str(remaining_ttl),
                },
            )

    return limiter