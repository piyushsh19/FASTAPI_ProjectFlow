
# tests/api/test_websocket_events.py

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
            "name": "Real-time Test Project",
            "description": "Testing task events",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_task_created_event(client):
    token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    project_id = create_project(client, token)

    with client.websocket_connect(
        f"/ws/projects/{project_id}?token={token}"
    ) as websocket:

        response = client.post(
            f"/projects/{project_id}/tasks",
            headers=auth_headers(token),
            json={
                "title": "Create real-time feature",
                "description": "Test task creation event",
                "status": "todo",
                "priority": "high",
            },
        )

        assert response.status_code == 201

        event = websocket.receive_json()

        assert event["type"] == "task.created"
        assert event["data"]["title"] == "Create real-time feature"


def test_task_updated_event(client):
    token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    project_id = create_project(client, token)

    task_response = client.post(
        f"/projects/{project_id}/tasks",
        headers=auth_headers(token),
        json={
            "title": "Original title",
            "status": "todo",
            "priority": "medium",
        },
    )

    task_id = task_response.json()["id"]

    with client.websocket_connect(
        f"/ws/projects/{project_id}?token={token}"
    ) as websocket:

        response = client.patch(
            f"/tasks/{task_id}",
            headers=auth_headers(token),
            json={"title": "Updated title"},
        )

        assert response.status_code == 200

        event = websocket.receive_json()

        assert event["type"] == "task.updated"
        assert event["data"]["title"] == "Updated title"


def test_task_deleted_event(client):
    token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    project_id = create_project(client, token)

    task_response = client.post(
        f"/projects/{project_id}/tasks",
        headers=auth_headers(token),
        json={
            "title": "Task to delete",
            "status": "todo",
            "priority": "low",
        },
    )

    task_id = task_response.json()["id"]

    with client.websocket_connect(
        f"/ws/projects/{project_id}?token={token}"
    ) as websocket:

        response = client.delete(
            f"/tasks/{task_id}",
            headers=auth_headers(token),
        )

        assert response.status_code == 204

        event = websocket.receive_json()

        assert event["type"] == "task.deleted"
