
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

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def get_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_project(client):
    token = register_and_login(client)

    response = client.post(
        "/projects/",
        headers=get_auth_headers(token),
        json={
            "name": "ProjectFlow Dashboard",
            "description": "Building a project management application",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "ProjectFlow Dashboard"
    assert data["description"] == "Building a project management application"
    assert data["owner_id"] > 0


def test_get_project(client):
    token = register_and_login(client)

    create_response = client.post(
        "/projects/",
        headers=get_auth_headers(token),
        json={
            "name": "Backend Project",
            "description": "FastAPI backend",
        },
    )

    project_id = create_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}",
        headers=get_auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_list_projects(client):
    token = register_and_login(client)

    headers = get_auth_headers(token)

    client.post(
        "/projects/",
        headers=headers,
        json={"name": "Project One", "description": "First project"},
    )

    client.post(
        "/projects/",
        headers=headers,
        json={"name": "Project Two", "description": "Second project"},
    )

    response = client.get("/projects/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_project(client):
    token = register_and_login(client)

    headers = get_auth_headers(token)

    create_response = client.post(
        "/projects/",
        headers=headers,
        json={"name": "Old Project Name", "description": "Old description"},
    )

    project_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}",
        headers=headers,
        json={"name": "Updated Project Name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project Name"


def test_delete_project(client):
    token = register_and_login(client)

    headers = get_auth_headers(token)

    create_response = client.post(
        "/projects/",
        headers=headers,
        json={"name": "Project To Delete", "description": "Temporary project"},
    )

    project_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/projects/{project_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/projects/{project_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_user_cannot_access_another_users_project(client):
    owner_token = register_and_login(
        client,
        "owner@example.com",
    )

    another_user_token = register_and_login(
        client,
        "another@example.com",
    )

    create_response = client.post(
        "/projects/",
        headers=get_auth_headers(owner_token),
        json={
            "name": "Private Project",
            "description": "Only the owner should access this",
        },
    )

    project_id = create_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}",
        headers=get_auth_headers(another_user_token),
    )

    assert response.status_code == 404
