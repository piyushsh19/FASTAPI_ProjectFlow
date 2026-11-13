
def register_and_login(client, email="owner@example.com"):
    """Register a user and return their JWT token."""

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Project Owner",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_project(client, token):
    response = client.post(
        "/projects/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Task Test Project",
            "description": "Project for testing tasks",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_task(client, token, project_id):
    response = client.post(
        f"/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Build authentication",
            "description": "Implement JWT authentication",
            "status": "todo",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_task(client):
    token = register_and_login(client)
    project_id = create_project(client, token)

    response = client.post(
        f"/projects/{project_id}/tasks",
        headers=auth_headers(token),
        json={
            "title": "Create API tests",
            "description": "Test task creation",
            "status": "todo",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Create API tests"
    assert response.json()["priority"] == "high"


def test_list_project_tasks(client):
    token = register_and_login(client)
    project_id = create_project(client, token)
    create_task(client, token, project_id)

    response = client.get(
        f"/projects/{project_id}/tasks",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["skip"] == 0
    assert data["limit"] == 20
    assert data["has_more"] is False


def test_get_task(client):
    token = register_and_login(client)
    project_id = create_project(client, token)
    task_id = create_task(client, token, project_id)

    response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(client):
    token = register_and_login(client)
    project_id = create_project(client, token)
    task_id = create_task(client, token, project_id)

    response = client.patch(
        f"/tasks/{task_id}",
        headers=auth_headers(token),
        json={"title": "Updated task title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task title"


def test_update_task_status(client):
    token = register_and_login(client)
    project_id = create_project(client, token)
    task_id = create_task(client, token, project_id)

    response = client.patch(
        f"/tasks/{task_id}/status",
        headers=auth_headers(token),
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_delete_task(client):
    token = register_and_login(client)
    project_id = create_project(client, token)
    task_id = create_task(client, token, project_id)

    response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404
