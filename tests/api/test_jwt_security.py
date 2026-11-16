
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def create_test_token(payload, secret=None):
    return jwt.encode(
        payload,
        secret or settings.secret_key,
        algorithm=settings.algorithm,
    )


def test_token_without_subject_is_rejected(client):
    token = create_test_token({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    })

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_without_expiration_is_rejected(client):
    token = create_test_token({
        "sub": "1",
    })

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_expired_token_is_rejected(client):
    token = create_test_token({
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    })

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_with_invalid_subject_is_rejected(client):
    token = create_test_token({
        "sub": "invalid-user-id",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    })

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_with_zero_user_id_is_rejected(client):
    token = create_test_token({
        "sub": "0",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    })

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_with_invalid_signature_is_rejected(client):
    token = create_test_token(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        secret="incorrect-test-secret",
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
