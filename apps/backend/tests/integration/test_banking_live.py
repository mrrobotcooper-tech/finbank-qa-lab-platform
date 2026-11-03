"""Live core-banking against Compose. Opt-in: FINBANK_INTEGRATION=1."""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

pytestmark = pytest.mark.integration

LIVE_API = os.environ.get("FINBANK_API_URL", "http://127.0.0.1:8000")
ANA = {"email": "ana@finbank.test", "password": "Customer1!"}
ADMIN = {"email": "admin@finbank.test", "password": "AdminPassw0rd"}
BRUNO_CHECKING = "32200000000000000003"


def _enabled() -> bool:
    return os.environ.get("FINBANK_INTEGRATION") == "1"


def _auth_headers(client: httpx.Client, credentials: dict[str, str]) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json=credentials)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.skipif(not _enabled(), reason="Set FINBANK_INTEGRATION=1 against a running stack")
def test_live_register_login_transfer_payment_and_admin_block() -> None:
    with httpx.Client(base_url=LIVE_API, timeout=15.0) as client:
        unique = uuid.uuid4().hex[:10]
        register = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"qa.{unique}@finbank.test",
                "password": "Customer1!",
                "full_name": "QA Registro",
            },
        )
        assert register.status_code == 201, register.text
        assert register.json()["role"] == "CUSTOMER"

        ana = _auth_headers(client, ANA)
        accounts = client.get("/api/v1/accounts", headers=ana)
        assert accounts.status_code == 200, accounts.text
        checking = next(item for item in accounts.json() if item["currency"] == "ARS")
        assert checking["available_balance"] >= 10_000

        transfer = client.post(
            "/api/v1/transfers",
            headers={**ana, "Idempotency-Key": f"it-{unique}"},
            json={
                "source_account_id": checking["id"],
                "destination_account_number": BRUNO_CHECKING,
                "amount": 10_000,
                "currency": "ARS",
            },
        )
        assert transfer.status_code == 201, transfer.text
        assert transfer.json()["status"] == "COMPLETED"

        replay = client.post(
            "/api/v1/transfers",
            headers={**ana, "Idempotency-Key": f"it-{unique}"},
            json={
                "source_account_id": checking["id"],
                "destination_account_number": BRUNO_CHECKING,
                "amount": 10_000,
                "currency": "ARS",
            },
        )
        assert replay.status_code == 201
        assert replay.json()["id"] == transfer.json()["id"]

        rejected = client.post(
            "/api/v1/payments",
            headers={**ana, "Idempotency-Key": f"pay-{unique}"},
            json={
                "account_id": checking["id"],
                "amount": 5_000,
                "currency": "ARS",
                "payment_type": "SERVICE",
                "payee": "REJECT",
            },
        )
        assert rejected.status_code == 201, rejected.text
        assert rejected.json()["status"] == "REJECTED"

        admin = _auth_headers(client, ADMIN)
        users = client.get("/api/v1/admin/users", headers=admin)
        assert users.status_code == 200
        emails = {item["email"] for item in users.json()}
        assert "ana@finbank.test" in emails

        try:
            blocked = client.patch(
                f"/api/v1/admin/accounts/{checking['id']}",
                headers=admin,
                json={"status": "BLOCKED"},
            )
            assert blocked.status_code == 200, blocked.text
            assert blocked.json()["status"] == "BLOCKED"
        finally:
            restored = client.patch(
                f"/api/v1/admin/accounts/{checking['id']}",
                headers=admin,
                json={"status": "ACTIVE"},
            )
            assert restored.status_code == 200
            assert restored.json()["status"] == "ACTIVE"

        audit = client.get("/api/v1/admin/audit", headers=admin)
        assert audit.status_code == 404
