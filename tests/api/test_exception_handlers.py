
def test_custom_application_exception(client):
    from app.core.exceptions import AppException

    @client.app.get("/test/custom-error")
    def custom_error():
        raise AppException(
            message="Project not found",
            status_code=404,
            error_code="PROJECT_NOT_FOUND",
        )

    response = client.get("/test/custom-error")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "PROJECT_NOT_FOUND"
    assert data["error"]["message"] == "Project not found"


def test_http_exception_handler(client):
    response = client.get("/notifications")

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"



def test_validation_exception_handler(client):
    # Register user
    client.post(
        "/auth/register",
        json={
            "name": "Validation Test User",
            "email": "validation@example.com",
            "password": "TestPassword123!",
        },
    )

    # Login and obtain JWT
    login_response = client.post(
        "/auth/login",
        data={
            "username": "validation@example.com",
            "password": "TestPassword123!",
        },
    )

    token = login_response.json()["access_token"]

    # Send invalid query parameter with authentication
    response = client.get(
        "/notifications?skip=-1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert len(data["error"]["details"]) > 0


def test_not_found_exception_handler(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"
