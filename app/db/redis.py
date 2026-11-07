
# app/db/redis.py

from redis.asyncio import Redis

from app.core.config import settings


def create_redis_client() -> Redis:
    """
    Create a Redis client with its own connection pool.
    """

    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


redis_client = create_redis_client()


async def close_redis() -> None:
    await redis_client.aclose()
