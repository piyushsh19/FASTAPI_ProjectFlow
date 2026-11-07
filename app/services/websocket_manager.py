
import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket

from app.db.redis import redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

        # One Redis listener task per project per process.
        self.listener_tasks: dict[int, asyncio.Task] = {}

    async def connect(
        self,
        websocket: WebSocket,
        project_id: int,
    ) -> None:
        await websocket.accept()
        self.active_connections[project_id].add(websocket)

        # Start a listener only when the first local client connects.
        if project_id not in self.listener_tasks:
            ready = asyncio.Event()

            task = asyncio.create_task(
                self._listen_to_project(project_id, ready)
            )

            self.listener_tasks[project_id] = task

            try:
                # Ensure Redis subscription is active before returning.
                await asyncio.wait_for(ready.wait(), timeout=5)

            except Exception:
                task.cancel()
                self.listener_tasks.pop(project_id, None)
                self.active_connections[project_id].discard(websocket)
                raise

    async def _listen_to_project(
        self,
        project_id: int,
        ready: asyncio.Event,
    ) -> None:
        channel = f"project:{project_id}"
        pubsub = redis_client.pubsub()

        try:
            await pubsub.subscribe(channel)
            logger.info("Subscribed to Redis channel: %s", channel)

            ready.set()

            async for message in pubsub.listen():

                if message["type"] != "message":
                    continue

                event = json.loads(message["data"])

                await self.broadcast_local(project_id, event)

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Redis listener failed for project %s",
                project_id,
            )

        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

    async def disconnect(
        self,
        websocket: WebSocket,
        project_id: int,
    ) -> None:
        connections = self.active_connections.get(project_id)

        if not connections:
            return

        connections.discard(websocket)

        # Stop the Redis listener when no local clients remain.
        if not connections:
            self.active_connections.pop(project_id, None)

            task = self.listener_tasks.pop(project_id, None)

            if task:
                task.cancel()

                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def broadcast_local(
        self,
        project_id: int,
        message: dict,
    ) -> None:
        connections = self.active_connections.get(project_id, set())

        disconnected = []

        for connection in list(connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            connections.discard(connection)


manager = ConnectionManager()
