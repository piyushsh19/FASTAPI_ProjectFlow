
import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket
from redis.asyncio import Redis

from app.db.redis import redis_client

logger = logging.getLogger(__name__)


class NotificationConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = (
            defaultdict(set)
        )
        self.listener_tasks: dict[int, asyncio.Task] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: int,
    ) -> None:
        await websocket.accept()

        self.active_connections[user_id].add(websocket)

        if user_id in self.listener_tasks:
            return

        ready = asyncio.Event()

        task = asyncio.create_task(
            self._listen_to_user(user_id, ready)
        )

        self.listener_tasks[user_id] = task

        try:
            await asyncio.wait_for(ready.wait(), timeout=5)

        except Exception:
            task.cancel()
            self.listener_tasks.pop(user_id, None)
            self.active_connections[user_id].discard(websocket)

            if not self.active_connections[user_id]:
                self.active_connections.pop(user_id, None)

            raise

    async def _listen_to_user(
        self,
        user_id: int,
        ready: asyncio.Event,
    ) -> None:
        channel = f"user:{user_id}:notifications"
        pubsub = redis_client.pubsub()

        try:
            await pubsub.subscribe(channel)

            logger.info(
                "Subscribed to notification channel: %s",
                channel,
            )

            ready.set()

            async for message in pubsub.listen():

                if message["type"] != "message":
                    continue

                event = json.loads(message["data"])

                await self.broadcast_local(user_id, event)

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Notification listener failed for user %s",
                user_id,
            )

        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

    async def disconnect(
        self,
        websocket: WebSocket,
        user_id: int,
    ) -> None:
        connections = self.active_connections.get(user_id)

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            self.active_connections.pop(user_id, None)

            task = self.listener_tasks.pop(user_id, None)

            if task:
                task.cancel()

                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def broadcast_local(
        self,
        user_id: int,
        message: dict,
    ) -> None:
        connections = self.active_connections.get(user_id, set())
        disconnected = []

        for connection in list(connections):
            try:
                await connection.send_json(message)

            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            connections.discard(connection)

    async def shutdown(self) -> None:
        tasks = list(self.listener_tasks.values())

        self.listener_tasks.clear()

        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        self.active_connections.clear()


notification_manager = NotificationConnectionManager()
