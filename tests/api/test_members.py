
# tests/api/test_members.py

def register_and_login(client, email, name):
    register_response = client.post(
        "/auth/register",
        json={
            "name": name,
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


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_project(client, token):
    response = client.post(
        "/projects/",
        headers=auth_headers(token),
        json={
            "name": "Membership Test Project",
            "description": "Testing project membership",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_owner_can_add_member(client):
    owner_token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    register_and_login(
        client, "member@example.com", "Project Member"
    )
    project_id = create_project(client, owner_token)

    response = client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "member"


def test_owner_can_list_members(client):
    owner_token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    register_and_login(
        client, "member@example.com", "Project Member"
    )
    project_id = create_project(client, owner_token)

    client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )

    response = client.get(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner_token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_owner_can_update_member_role(client):
    owner_token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    member_token = register_and_login(
        client, "member@example.com", "Project Member"
    )
    project_id = create_project(client, owner_token)

    member_response = client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )
    assert member_response.status_code == 201

    member_user_id = member_response.json()["user_id"]

    response = client.patch(
        f"/projects/{project_id}/members/{member_user_id}",
        headers=auth_headers(owner_token),
        json={"role": "viewer"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "viewer"


def test_owner_can_remove_member(client):
    owner_token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    register_and_login(
        client, "member@example.com", "Project Member"
    )
    project_id = create_project(client, owner_token)

    member_response = client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )
    assert member_response.status_code == 201

    member_user_id = member_response.json()["user_id"]

    response = client.delete(
        f"/projects/{project_id}/members/{member_user_id}",
        headers=auth_headers(owner_token),
    )

    assert response.status_code == 204


def test_non_owner_cannot_add_member(client):
    owner_token = register_and_login(
        client, "owner@example.com", "Project Owner"
    )
    member_token = register_and_login(
        client, "member@example.com", "Project Member"
    )
    register_and_login(
        client, "newmember@example.com", "New Member"
    )

    project_id = create_project(client, owner_token)

    client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(owner_token),
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )

    response = client.post(
        f"/projects/{project_id}/members",
        headers=auth_headers(member_token),
        json={
            "email": "newmember@example.com",
            "role": "member",
        },
    )

    assert response.status_code == 403
