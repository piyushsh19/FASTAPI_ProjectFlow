
def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    payload = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
    }

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_success(client):
    # First register the user.
    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "TestPassword123!",
        },
    )

    # OAuth2PasswordRequestForm expects form fields,
    # not a JSON request body.
    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "wrong-password@example.com",
            "password": "CorrectPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "wrong-password@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_get_current_user(client):
    # Register a user.
    client.post(
        "/auth/register",
        json={
            "name": "Current User",
            "email": "current@example.com",
            "password": "TestPassword123!",
        },
    )

    # Login and obtain JWT.
    login_response = client.post(
        "/auth/login",
        data={
            "username": "current@example.com",
            "password": "TestPassword123!",
        },
    )

    token = login_response.json()["access_token"]

    # Call protected endpoint.
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Current User"
    assert data["email"] == "current@example.com"


def test_get_current_user_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401
