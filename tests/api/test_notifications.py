
import pytest

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.notification import Notification


def register_and_login(client, name: str, email: str):
    """Register a user and return their JWT access token."""

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


def insert_notification(
    db_session: Session,
    user_id: int,
    title: str = "Task assigned",
    is_read: bool = False,
):
    """Insert a notification directly into the test database."""

    notification = Notification(
        user_id=user_id,
        type="task_assigned",
        title=title,
        message="You have been assigned a task.",
        data={"task_id": 101},
        is_read=is_read,
    )

    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)

    return notification


@pytest.fixture
def notification_users(client, db_session):
    """Create two users and their authentication tokens."""

    token1 = register_and_login(
        client,
        "Notification User 1",
        "notification1@example.com",
    )

    token2 = register_and_login(
        client,
        "Notification User 2",
        "notification2@example.com",
    )

    user1 = db_session.query(User).filter_by(
        email="notification1@example.com"
    ).one()

    user2 = db_session.query(User).filter_by(
        email="notification2@example.com"
    ).one()

    return {
        "user1": user1,
        "user2": user2,
        "token1": token1,
        "token2": token2,
    }


def test_get_notifications(client, db_session, notification_users):
    user = notification_users["user1"]
    token = notification_users["token1"]

    insert_notification(db_session, user.id)
    insert_notification(
        db_session,
        user.id,
        title="Project invitation",
    )

    response = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["unread_count"] == 2
    assert len(data["notifications"]) == 2


def test_notifications_are_isolated_between_users(
    client,
    db_session,
    notification_users,
):
    user1 = notification_users["user1"]
    user2 = notification_users["user2"]
    token1 = notification_users["token1"]

    insert_notification(db_session, user1.id)
    insert_notification(db_session, user2.id)

    response = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token1}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    for notification in data["notifications"]:
        assert notification["user_id"] == user1.id


def test_get_notifications_pagination(
    client,
    db_session,
    notification_users,
):
    user = notification_users["user1"]
    token = notification_users["token1"]

    for index in range(5):
        insert_notification(
            db_session,
            user.id,
            title=f"Notification {index}",
        )

    response = client.get(
        "/notifications?skip=0&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["notifications"]) == 2
    assert data["total"] == 5


def test_get_unread_count(client, db_session, notification_users):
    user = notification_users["user1"]
    token = notification_users["token1"]

    insert_notification(db_session, user.id)
    insert_notification(db_session, user.id)
    insert_notification(
        db_session,
        user.id,
        is_read=True,
    )

    response = client.get(
        "/notifications/unread-count",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["unread_count"] == 2


def test_mark_notification_as_read(
    client,
    db_session,
    notification_users,
):
    user = notification_users["user1"]
    token = notification_users["token1"]

    notification = insert_notification(db_session, user.id)

    response = client.patch(
        f"/notifications/{notification.id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == notification.id
    assert response.json()["is_read"] is True


def test_user_cannot_mark_another_users_notification_as_read(
    client,
    db_session,
    notification_users,
):
    user2 = notification_users["user2"]
    token1 = notification_users["token1"]

    notification = insert_notification(db_session, user2.id)

    response = client.patch(
        f"/notifications/{notification.id}/read",
        headers={"Authorization": f"Bearer {token1}"},
    )

    assert response.status_code == 404


def test_mark_all_notifications_as_read(
    client,
    db_session,
    notification_users,
):
    user = notification_users["user1"]
    token = notification_users["token1"]

    insert_notification(db_session, user.id)
    insert_notification(db_session, user.id)

    response = client.patch(
        "/notifications/read-all",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["updated_count"] == 2

    unread_response = client.get(
        "/notifications/unread-count",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert unread_response.json()["unread_count"] == 0


def test_delete_notification(
    client,
    db_session,
    notification_users,
):
    user = notification_users["user1"]
    token = notification_users["token1"]

    notification = insert_notification(db_session, user.id)

    response = client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    list_response = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert list_response.json()["total"] == 0


def test_user_cannot_delete_another_users_notification(
    client,
    db_session,
    notification_users,
):
    user2 = notification_users["user2"]
    token1 = notification_users["token1"]

    notification = insert_notification(db_session, user2.id)

    response = client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )

    assert response.status_code == 404


def test_notifications_require_authentication(client):
    response = client.get("/notifications")

    assert response.status_code == 401
