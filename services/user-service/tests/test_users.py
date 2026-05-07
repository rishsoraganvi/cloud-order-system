import os
import pytest
from fastapi.testclient import TestClient


def make_app():
    # Use in-memory SQLite for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    # Import the package-based app (services.user_service)
    from services.user_service.app.main import create_app
    app = create_app(database_url=os.environ["DATABASE_URL"])
    return app


@pytest.fixture
def client():
    app = make_app()
    with TestClient(app) as c:
        yield c


def test_register_login_and_me(client):
    # Register
    resp = client.post("/users/register", json={"email": "alice@example.com", "password": "secret"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    user_id = body["id"]

    # Login
    resp = client.post("/users/login", json={"email": "alice@example.com", "password": "secret"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token

    # /me without token
    resp = client.get("/users/me")
    assert resp.status_code == 401

    # /me with token
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == user_id
    assert body["email"] == "alice@example.com"
