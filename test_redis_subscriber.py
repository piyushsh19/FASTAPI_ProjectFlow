
# test_redis_subscriber.py

import asyncio

from app.db.redis import redis_client
from app.services.redis_publisher import publish_project_event
from app.services.redis_subscriber import subscribe_to_project


async def main():
    project_id = 99

    subscriber = subscribe_to_project(
        redis_client,
        project_id,
    )

    try:
        # Start the subscriber and wait for its subscription.
        event_iterator = subscriber.__aiter__()

        event_task = asyncio.create_task(
            event_iterator.__anext__()
        )

        # Give Redis time to register the subscription.
        await asyncio.sleep(0.2)

        event = {
            "type": "task.created",
            "project_id": project_id,
            "task": {
                "id": 10,
                "title": "Test Redis subscriber",
            },
        }

        await publish_project_event(project_id, event)

        received_event = await asyncio.wait_for(
            event_task,
            timeout=5,
        )

        print("Received event:", received_event)

        assert received_event == event

        print("Redis Pub/Sub test successful!")

    finally:
        await subscriber.aclose()
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
