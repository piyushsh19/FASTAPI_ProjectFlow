from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Each project has its own set of connected WebSocket clients.
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(
        self,
        websocket: WebSocket,
        project_id: int,
    ) -> None:
        await websocket.accept()
        self.active_connections[project_id].add(websocket)

    def disconnect(
        self,
        websocket: WebSocket,
        project_id: int,
    ) -> None:
        connections = self.active_connections.get(project_id)

        if connections:
            connections.discard(websocket)

            if not connections:
                self.active_connections.pop(project_id, None)

    async def broadcast(
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
            self.disconnect(connection, project_id)


manager = ConnectionManager()