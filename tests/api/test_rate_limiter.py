def test_login_allows_requests_within_limit(client):
    for _ in range(5):
        response = client.post(
            "/auth/login",
            data={
                "username": "unknown@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401


def test_login_blocks_requests_after_limit(client):
    for _ in range(5):
        client.post(
            "/auth/login",
            data={
                "username": "unknown@example.com",
                "password": "WrongPassword123!",
            },
        )

    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "TOO_MANY_REQUESTS"
    assert "Retry-After" in response.headers


def test_registration_has_independent_rate_limit(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Rate Limit User",
            "email": "rate-limit-user@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201