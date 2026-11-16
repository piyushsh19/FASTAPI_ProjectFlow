
def register_and_login(client, email, name):
    response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200

    return response.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_project(client, token):
    response = client.post(
        "/projects/",
        headers=headers(token),
        json={
            "name": "RBAC Test Project",
            "description": "Project for RBAC tests",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def add_member(client, project_id, owner_token, email, role):
    return client.post(
        f"/projects/{project_id}/members",
        headers=headers(owner_token),
        json={"email": email, "role": role},
    )


def test_member_can_view_shared_project(client):
    owner = register_and_login(
        client, "owner_rbac@example.com", "Owner"
    )
    member = register_and_login(
        client, "member_rbac@example.com", "Member"
    )

    project_id = create_project(client, owner)

    response = add_member(
        client, project_id, owner,
        "member_rbac@example.com", "member"
    )
    assert response.status_code == 201

    response = client.get(
        f"/projects/{project_id}",
        headers=headers(member),
    )

    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_member_sees_shared_project_in_project_list(client):
    owner = register_and_login(
        client, "owner_list@example.com", "Owner"
    )
    member = register_and_login(
        client, "member_list@example.com", "Member"
    )

    project_id = create_project(client, owner)

    response = add_member(
        client, project_id, owner,
        "member_list@example.com", "member"
    )
    assert response.status_code == 201

    response = client.get(
        "/projects/",
        headers=headers(member),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == project_id


def test_non_member_cannot_view_project(client):
    owner = register_and_login(
        client, "owner_private@example.com", "Owner"
    )
    outsider = register_and_login(
        client, "outsider_private@example.com", "Outsider"
    )

    project_id = create_project(client, owner)

    response = client.get(
        f"/projects/{project_id}",
        headers=headers(outsider),
    )

    assert response.status_code == 404


def test_admin_can_update_project(client):
    owner = register_and_login(
        client, "owner_update@example.com", "Owner"
    )
    admin = register_and_login(
        client, "admin_update@example.com", "Admin"
    )

    project_id = create_project(client, owner)

    response = add_member(
        client, project_id, owner,
        "admin_update@example.com", "admin"
    )
    assert response.status_code == 201

    response = client.patch(
        f"/projects/{project_id}",
        headers=headers(admin),
        json={"name": "Updated by Admin"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated by Admin"


def test_admin_can_manage_project_members(client):
    owner = register_and_login(
        client, "owner_manage@example.com", "Owner"
    )
    admin = register_and_login(
        client, "admin_manage@example.com", "Admin"
    )
    new_member = register_and_login(
        client, "new_member@example.com", "New Member"
    )

    project_id = create_project(client, owner)

    response = add_member(
        client, project_id, owner,
        "admin_manage@example.com", "admin"
    )
    assert response.status_code == 201

    response = client.post(
        f"/projects/{project_id}/members",
        headers=headers(admin),
        json={
            "email": "new_member@example.com",
            "role": "member",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "member"


def test_admin_cannot_delete_project(client):
    owner = register_and_login(
        client, "owner_delete@example.com", "Owner"
    )
    admin = register_and_login(
        client, "admin_delete@example.com", "Admin"
    )

    project_id = create_project(client, owner)

    response = add_member(
        client, project_id, owner,
        "admin_delete@example.com", "admin"
    )
    assert response.status_code == 201

    response = client.delete(
        f"/projects/{project_id}",
        headers=headers(admin),
    )

    assert response.status_code == 403

    # The project must still exist for its owner.
    response = client.get(
        f"/projects/{project_id}",
        headers=headers(owner),
    )
    assert response.status_code == 200


def test_viewer_cannot_update_project(client):
    owner = register_and_login(
        client, "owner_viewer@example.com", "Owner"
    )
    viewer = register_and_login(
        client, "viewer_update@example.com", "Viewer"
    )

    project_id = create_project(client, owner)

    response = add_member(
        client, project_id, owner,
        "viewer_update@example.com", "viewer"
    )
    assert response.status_code == 201

    response = client.patch(
        f"/projects/{project_id}",
        headers=headers(viewer),
        json={"name": "Unauthorized update"},
    )

    assert response.status_code == 403
