
def test_allowed_cors_origin(client):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )


def test_disallowed_cors_origin(client):
    response = client.options(
        "/health/live",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    # The preflight request must not be granted permission.
    assert (
        "access-control-allow-origin"
        not in response.headers
    )


def test_security_headers(client):
    response = client.get("/health/live")

    assert response.status_code == 200

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"

    assert (
        response.headers["referrer-policy"]
        == "strict-origin-when-cross-origin"
    )

    assert (
        response.headers["permissions-policy"]
        == "camera=(), microphone=(), geolocation=()"
    )


def test_hsts_not_enabled_in_development(client):
    response = client.get("/health/live")

    assert "strict-transport-security" not in response.headers
