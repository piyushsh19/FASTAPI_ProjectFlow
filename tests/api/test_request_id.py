import uuid


def test_request_generates_request_id(client):
    response = client.get("/")

    assert response.status_code == 200

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None

    # Verify that the generated ID is a valid UUID.
    uuid.UUID(request_id)


def test_request_accepts_valid_request_id(client):
    request_id = str(uuid.uuid4())

    response = client.get(
        "/",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_request_replaces_invalid_request_id(client):
    response = client.get(
        "/",
        headers={"X-Request-ID": "invalid-request-id"},
    )

    assert response.status_code == 200

    generated_id = response.headers["X-Request-ID"]

    assert generated_id != "invalid-request-id"
    uuid.UUID(generated_id)


def test_request_id_is_returned_for_http_errors(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
    assert "X-Request-ID" in response.headers

    uuid.UUID(response.headers["X-Request-ID"])