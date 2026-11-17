
import pytest


PASSWORD = "TestPassword123!"


def register_and_login(client, email, name):
    response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": PASSWORD,
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
            "name": "Task RBAC Project",
            "description": "Project for task authorization tests",
        },
    )
    assert response.status_code == 201

    return response.json()["id"]


def add_member(client, project_id, owner_token, email, role):
    response = client.post(
        f"/projects/{project_id}/members",
        headers=headers(owner_token),
        json={"email": email, "role": role},
    )
    assert response.status_code == 201
    return response


def create_task(client, project_id, token):
    response = client.post(
        f"/projects/{project_id}/tasks",
        headers=headers(token),
        json={
            "title": "Task RBAC Test",
            "description": "Testing task permissions",
            "priority": "high",
        },
    )
    assert response.status_code == 201

    return response.json()["id"]


def setup_project_with_role(client, role, suffix):
    owner_token = register_and_login(
        client,
        f"owner_{suffix}@example.com",
        "Project Owner",
    )

    user_email = f"{role}_{suffix}@example.com"

    user_token = register_and_login(
        client,
        user_email,
        f"Project {role.title()}",
    )

    project_id = create_project(client, owner_token)

    add_member(
        client,
        project_id,
        owner_token,
        user_email,
        role,
    )

    return owner_token, user_token, project_id


def test_viewer_can_read_project_tasks(client):
    owner, viewer, project_id = setup_project_with_role(
        client, "viewer", "read"
    )

    task_id = create_task(client, project_id, owner)

    list_response = client.get(
        f"/projects/{project_id}/tasks",
        headers=headers(viewer),
    )

    detail_response = client.get(
        f"/tasks/{task_id}",
        headers=headers(viewer),
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == task_id


@pytest.mark.parametrize(
    "operation",
    ["create", "update", "status", "delete"],
)
def test_viewer_cannot_modify_tasks(client, operation):
    owner, viewer, project_id = setup_project_with_role(
        client, "viewer", f"deny_{operation}"
    )

    task_id = create_task(client, project_id, owner)

    if operation == "create":
        response = client.post(
            f"/projects/{project_id}/tasks",
            headers=headers(viewer),
            json={
                "title": "Unauthorized task",
                "priority": "high",
            },
        )

    elif operation == "update":
        response = client.patch(
            f"/tasks/{task_id}",
            headers=headers(viewer),
            json={"title": "Unauthorized update"},
        )

    elif operation == "status":
        response = client.patch(
            f"/tasks/{task_id}/status",
            headers=headers(viewer),
            json={"status": "done"},
        )

    else:
        response = client.delete(
            f"/tasks/{task_id}",
            headers=headers(viewer),
        )

    assert response.status_code == 403


def test_member_can_create_update_and_change_task_status(client):
    _, member, project_id = setup_project_with_role(
        client, "member", "member_permissions"
    )

    task_id = create_task(client, project_id, member)

    update_response = client.patch(
        f"/tasks/{task_id}",
        headers=headers(member),
        json={"title": "Updated by member"},
    )

    status_response = client.patch(
        f"/tasks/{task_id}/status",
        headers=headers(member),
        json={"status": "in_progress"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated by member"

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "in_progress"


def test_member_cannot_delete_task(client):
    owner, member, project_id = setup_project_with_role(
        client, "member", "member_delete"
    )

    task_id = create_task(client, project_id, owner)

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers(member),
    )

    assert response.status_code == 403

    # Verify that the task still exists.
    get_response = client.get(
        f"/tasks/{task_id}",
        headers=headers(owner),
    )

    assert get_response.status_code == 200


def test_admin_can_delete_task(client):
    owner, admin, project_id = setup_project_with_role(
        client, "admin", "admin_delete"
    )

    task_id = create_task(client, project_id, owner)

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers(admin),
    )

    assert response.status_code == 204


def test_viewer_cannot_be_assigned_a_task(client):
    owner, viewer, project_id = setup_project_with_role(
        client, "viewer", "viewer_assignment"
    )

    # Get the viewer's user ID from the project member list.
    members_response = client.get(
        f"/projects/{project_id}/members",
        headers=headers(owner),
    )

    assert members_response.status_code == 200

    viewer_member = next(
        member
        for member in members_response.json()
        if member["role"] == "viewer"
    )

    response = client.post(
        f"/projects/{project_id}/tasks",
        headers=headers(owner),
        json={
            "title": "Assign to viewer",
            "priority": "medium",
            "assigned_to": viewer_member["user_id"],
        },
    )

    assert response.status_code == 400


def test_non_member_cannot_access_project_tasks(client):
    owner = register_and_login(
        client,
        "owner_nonmember@example.com",
        "Owner",
    )

    outsider = register_and_login(
        client,
        "outsider_nonmember@example.com",
        "Outsider",
    )

    project_id = create_project(client, owner)
    task_id = create_task(client, project_id, owner)

    list_response = client.get(
        f"/projects/{project_id}/tasks",
        headers=headers(outsider),
    )

    detail_response = client.get(
        f"/tasks/{task_id}",
        headers=headers(outsider),
    )

    assert list_response.status_code == 404
    assert detail_response.status_code == 404
