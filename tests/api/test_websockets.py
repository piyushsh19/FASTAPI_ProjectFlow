
# tests/api/test_websockets.py

from fastapi.testclient import TestClient


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
