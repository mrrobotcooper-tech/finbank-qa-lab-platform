from fastapi.testclient import TestClient

from finbank.mocks.app import app


def test_mocks_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "finbank-mocks"


def test_mocks_approve_generic_payee() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/charges",
            json={"amount": 1000, "currency": "ARS", "reference": "pay-1", "payee": "AYSA"},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_mocks_reject_named_payee() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/charges",
            json={"amount": 1000, "currency": "ARS", "reference": "pay-2", "payee": "REJECT"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "GATEWAY_REJECTED"
