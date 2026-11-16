
import pytest
from pydantic import ValidationError

from app.core.security import hash_password, verify_password
from app.schemas.user import UserCreate


def test_password_must_have_at_least_12_characters():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="short@example.com",
            password="Short123",
        )


def test_password_cannot_exceed_128_characters():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="long@example.com",
            password="A" * 129,
        )


def test_password_cannot_contain_only_whitespace():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="blank@example.com",
            password=" " * 12,
        )


def test_valid_password_is_accepted():
    user = UserCreate(
        name="Test User",
        email="valid@example.com",
        password="MyStrongPassword123!",
    )

    assert user.password == "MyStrongPassword123!"


def test_password_is_hashed():
    password = "MyStrongPassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2id$")


def test_password_hash_can_be_verified():
    password = "MyStrongPassword123!"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


def test_incorrect_password_is_rejected():
    hashed_password = hash_password("MyStrongPassword123!")

    assert not verify_password(
        "IncorrectPassword123!",
        hashed_password,
    )


def test_same_password_produces_different_hashes():
    password = "MyStrongPassword123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash

    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_registration_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "short-password@example.com",
            "password": "Short123",
        },
    )

    assert response.status_code == 422


def test_login_returns_same_error_for_unknown_and_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "password-check@example.com",
            "password": "CorrectPassword123!",
        },
    )

    unknown_user_response = client.post(
        "/auth/login",
        data={
            "username": "unknown-password@example.com",
            "password": "WrongPassword123!",
        },
    )

    wrong_password_response = client.post(
        "/auth/login",
        data={
            "username": "password-check@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert unknown_user_response.status_code == 401
    assert wrong_password_response.status_code == 401

    assert unknown_user_response.json() == wrong_password_response.json()
