
# app/services/redis_subscriber.py

import json
import logging

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def subscribe_to_project(
    redis_client: Redis,
    project_id: int,
):
    """
    Listen for events published to a project-specific channel.
    """

    channel = f"project:{project_id}"

    pubsub = redis_client.pubsub()

    await pubsub.subscribe(channel)

    logger.info("Subscribed to Redis channel: %s", channel)

    try:
        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            event = json.loads(message["data"])

            logger.info(
                "Received event from %s: %s",
                channel,
                event,
            )

            yield event

    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
