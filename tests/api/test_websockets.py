
# tests/api/test_websockets.py
import pytest
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

def register_and_login(client, email, name):
    client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": "TestPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_project(client, token):
    response = client.post(
        "/projects/",
        headers=auth_headers(token),
        json={
            "name": "WebSocket Test Project",
            "description": "Testing WebSocket connections",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_websocket_ping_pong(client):
    token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    project_id = create_project(client, token)

    with client.websocket_connect(
        f"/ws/projects/{project_id}?token={token}"
    ) as websocket:
        websocket.send_text("ping")

        response = websocket.receive_json()

        assert response == {"type": "pong"}


def test_websocket_rejects_missing_token(client):
    token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    project_id = create_project(client, token)

    try:
        with client.websocket_connect(
            f"/ws/projects/{project_id}"
        ):
            assert False, "Connection should have been rejected"
    except Exception:
        pass


def test_websocket_rejects_invalid_token(client):
    token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    project_id = create_project(client, token)

    try:
        with client.websocket_connect(
            f"/ws/projects/{project_id}?token=invalid-token"
        ):
            assert False, "Connection should have been rejected"
    except Exception:
        pass

def test_viewer_can_connect_to_project_websocket(client):
    owner = register_and_login(
        client,
        "ws_owner_viewer@example.com",
        "Owner",
    )
    viewer = register_and_login(
        client,
        "ws_viewer@example.com",
        "Viewer",
    )

    project_id = create_project(client, owner)

    response = client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner),
        json={
            "email": "ws_viewer@example.com",
            "role": "viewer",
        },
    )

    assert response.status_code == 201

    with client.websocket_connect(
        f"/ws/projects/{project_id}?token={viewer}"
    ) as websocket:
        websocket.send_text("ping")
        assert websocket.receive_json() == {"type": "pong"}


def test_non_member_cannot_connect_to_project_websocket(client):
    owner = register_and_login(
        client,
        "ws_private_owner@example.com",
        "Owner",
    )
    outsider = register_and_login(
        client,
        "ws_outsider@example.com",
        "Outsider",
    )

    project_id = create_project(client, owner)

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(
            f"/ws/projects/{project_id}?token={outsider}"
        ):
            pass

    assert exc.value.code == 4403


def test_project_websocket_rejects_expired_token(client):
    owner = register_and_login(
        client,
        "ws_expired_owner@example.com",
        "Owner",
    )

    project_id = create_project(client, owner)

    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(
            f"/ws/projects/{project_id}?token={expired_token}"
        ):
            pass

    assert exc.value.code == 4403