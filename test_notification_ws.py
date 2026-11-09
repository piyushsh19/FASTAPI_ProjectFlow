
import asyncio
import json
import websockets

from redis.asyncio import Redis


USER_ID = 5  # Replace with the ID of your test user.
TOKEN = "YOUR_JWT_TOKEN"

WS_URL = (
    f"ws://127.0.0.1:8001/ws/notifications"
    f"?token={TOKEN}"
)


async def main():
    redis = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected to notification WebSocket")

            # Test ping/pong first.
            await websocket.send("ping")
            response = json.loads(await websocket.recv())

            assert response["type"] == "pong"
            print("Ping/pong successful")

            # Publish a test notification directly to Redis.
            event = {
                "type": "notification.created",
                "notification": {
                    "id": 101,
                    "user_id": USER_ID,
                    "title": "Test notification",
                    "message": "Redis notification delivery works!",
                    "is_read": False,
                },
            }

            await redis.publish(
                f"user:{USER_ID}:notifications",
                json.dumps(event),
            )

            received = json.loads(
                await asyncio.wait_for(
                    websocket.recv(),
                    timeout=10,
                )
            )

            print("Received:", received)

            assert received["type"] == "notification.created"
            assert received["notification"]["user_id"] == USER_ID

            print("SUCCESS: User notification delivered!")

    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
