
import pytest
import redis

from fastapi import WebSocketDisconnect

from app.core.config import settings
from app.models.user import User


def register_and_login(client, email):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Notification WS User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


@pytest.fixture
def notification_ws_user(client, db_session):
    email = "notification-ws@example.com"

    token = register_and_login(client, email)

    user = db_session.query(User).filter_by(
        email=email
    ).one()

    return {
        "user": user,
        "token": token,
    }


def test_notification_websocket_ping_pong(
    client,
    notification_ws_user,
):
    token = notification_ws_user["token"]

    with client.websocket_connect(
        f"/ws/notifications?token={token}"
    ) as websocket:
        websocket.send_text("ping")

        response = websocket.receive_json()

        assert response == {"type": "pong"}


def test_notification_websocket_invalid_token(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(
            "/ws/notifications?token=invalid-token"
        ):
            pass

    assert exc.value.code == 4401


def test_notification_websocket_missing_token(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/notifications"):
            pass


def test_notification_websocket_receives_redis_event(
    client,
    notification_ws_user,
):
    token = notification_ws_user["token"]
    user_id = notification_ws_user["user"].id

    event = {
        "type": "notification.created",
        "notification": {
            "id": 101,
            "user_id": user_id,
            "type": "task_assigned",
            "title": "Task assigned",
            "message": "You have been assigned a task.",
            "data": {"task_id": 101},
            "is_read": False,
        },
    }

    # A synchronous Redis client is used by the test.
    # The application itself continues using redis.asyncio.
    redis_test_client = redis.Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        with client.websocket_connect(
            f"/ws/notifications?token={token}"
        ) as websocket:

            # The WebSocket manager has subscribed to Redis
            # before websocket_connect returns.
            redis_test_client.publish(
                f"user:{user_id}:notifications",
                __import__("json").dumps(event),
            )

            response = websocket.receive_json()

            assert response["type"] == "notification.created"
            assert response["notification"]["user_id"] == user_id
            assert response["notification"]["title"] == "Task assigned"

    finally:
        redis_test_client.close()
