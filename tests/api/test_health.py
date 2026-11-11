def test_liveness_check(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "alive",
    }


def test_readiness_check(client):
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["redis"] == "ok"