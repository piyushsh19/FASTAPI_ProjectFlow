
import asyncio

from app.services.notification_websocket_manager import (
    NotificationConnectionManager,
)


class FakeWebSocket:
    def __init__(self):
        self.messages = []

    async def send_json(self, message):
        self.messages.append(message)


def test_notification_broadcast_is_isolated_by_user():
    async def run_test():
        manager = NotificationConnectionManager()

        user_a_socket = FakeWebSocket()
        user_b_socket = FakeWebSocket()

        manager.active_connections[101].add(user_a_socket)
        manager.active_connections[202].add(user_b_socket)

        event = {
            "type": "notification.created",
            "notification": {
                "user_id": 101,
                "title": "Private notification",
            },
        }

        await manager.broadcast_local(101, event)

        assert user_a_socket.messages == [event]
        assert user_b_socket.messages == []

    asyncio.run(run_test())
