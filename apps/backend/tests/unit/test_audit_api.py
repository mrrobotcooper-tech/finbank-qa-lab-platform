from fastapi.testclient import TestClient


def test_admin_audit_is_not_exposed(client: TestClient) -> None:
    response = client.get("/api/v1/admin/audit")
    assert response.status_code == 404
    assert "audit" in response.json()["detail"].lower()
