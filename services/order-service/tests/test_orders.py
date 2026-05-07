import os
import pytest
from fastapi.testclient import TestClient


def make_app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    from services.order_service.app.main import create_app
    app = create_app(database_url=os.environ["DATABASE_URL"])
    return app


@pytest.fixture
def client():
    app = make_app()
    with TestClient(app) as c:
        yield c


def test_place_order(client):
    # Test 1: POST /orders with valid product_id and qty creates order with PENDING status
    resp = client.post("/orders", json={"product_id": 1, "qty": 5})
    assert resp.status_code == 201
    body = resp.json()
    assert body["product_id"] == 1
    assert body["qty"] == 5
    assert body["status"] == "PENDING"
    order_id = body["id"]


def test_get_order(client):
    # First create an order
    resp = client.post("/orders", json={"product_id": 1, "qty": 5})
    assert resp.status_code == 201
    order_id = resp.json()["id"]

    # Test 2: GET /orders/{id} returns order with correct data
    resp = client.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == order_id
    assert body["status"] == "PENDING"

    # Test 2b: Invalid id returns 404
    resp = client.get("/orders/99999")
    assert resp.status_code == 404


def test_valid_state_transition(client):
    # First create an order
    resp = client.post("/orders", json={"product_id": 1, "qty": 5})
    assert resp.status_code == 201
    order_id = resp.json()["id"]

    # Test 3: PATCH /orders/{id}/status with valid transition (PENDING→CONFIRMED)
    resp = client.patch(f"/orders/{order_id}/status", json={"status": "CONFIRMED"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "CONFIRMED"


def test_invalid_state_transition(client):
    # First create an order
    resp = client.post("/orders", json={"product_id": 1, "qty": 5})
    assert resp.status_code == 201
    order_id = resp.json()["id"]

    # Test 4: Invalid state transition (PENDING→DELIVERED) returns 400
    resp = client.patch(f"/orders/{order_id}/status", json={"status": "DELIVERED"})
    assert resp.status_code == 400
    body = resp.json()
    assert "error" in body or "detail" in body
