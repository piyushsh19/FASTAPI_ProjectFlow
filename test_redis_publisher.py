
# test_redis_publisher.py

import asyncio

from app.db.redis import redis_client
from app.services.redis_publisher import publish_project_event


async def main():
    project_id = 22

    event = {
        "type": "task.created",
        "project_id": project_id,
        "task": {
            "id": 1,
            "title": "Build Redis integration",
        },
    }

    try:
        await publish_project_event(project_id, event)
        print("Event published successfully!")

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
