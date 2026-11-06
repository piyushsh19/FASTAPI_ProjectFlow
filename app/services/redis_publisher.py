
# app/services/redis_publisher.py

import json

from app.db.redis import redis_client


async def publish_project_event(
    project_id: int,
    event: dict,
) -> None:
    """
    Publish an event to a project-specific Redis channel.
    """

    channel = f"project:{project_id}"

    message = json.dumps(event)

    await redis_client.publish(channel, message)

    print(f"Published event to Redis channel: {channel}")
