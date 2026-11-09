
import json
import logging

from app.db.redis import redis_client

logger = logging.getLogger(__name__)


async def publish_notification(
    user_id: int,
    notification: dict,
) -> None:
    channel = f"user:{user_id}:notifications"

    await redis_client.publish(
        channel,
        json.dumps(notification),
    )

    logger.info(
        "Published notification to Redis channel: %s",
        channel,
    )
