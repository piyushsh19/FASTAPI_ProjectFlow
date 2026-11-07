
# app/services/redis_publisher.py

import json

from redis.asyncio import Redis

from app.db.redis import redis_client


async def publish_project_event(
    project_id: int,
    event: dict,
    client: Redis | None = None,
) -> None:
    redis = client or redis_client

    channel = f"project:{project_id}"

    await redis.publish(
        channel,
        json.dumps(event),
    )
