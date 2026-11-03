from fastapi.testclient import TestClient
from tests.fakes import FakeChecker

from finbank.core.config import Settings
from finbank.main import create_app
from finbank.services.health import HealthService


def test_liveness_does_not_depend_on_infrastructure(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "finbank"
    assert body["correlation_id"]


def test_liveness_echoes_incoming_correlation_id(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Correlation-ID": "qa-trace-1"})
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "qa-trace-1"
    assert response.json()["correlation_id"] == "qa-trace-1"


def test_ready_ok_when_all_components_up(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    names = {item["name"] for item in body["components"]}
    assert names == {"postgres", "redis", "rabbitmq"}


def test_ready_returns_503_when_postgres_is_down() -> None:
    settings = Settings(app_env="test")
    health = HealthService(
        [
            FakeChecker("postgres", status="down", detail="timeout"),
            FakeChecker("redis"),
            FakeChecker("rabbitmq"),
        ]
    )
    app = create_app(settings, health_service=health)
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    postgres = next(item for item in body["components"] if item["name"] == "postgres")
    assert postgres["status"] == "down"
    assert postgres["detail"] == "timeout"


def test_metrics_exposes_prometheus_text(client: TestClient) -> None:
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "finbank_http_requests_total" in response.text


def test_security_headers_are_present(client: TestClient) -> None:
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert "camera=()" in response.headers["Permissions-Policy"]


def test_api_v1_health_alias(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
