from __future__ import annotations

from fastapi.testclient import TestClient

from finbank.adapters.rabbitmq import RabbitChecker
from finbank.core.config import Settings
from finbank.workers.main import create_worker_app


class _StubRabbit(RabbitChecker):
    def __init__(self, connected: bool) -> None:
        self._connected = connected

    def is_connected(self) -> bool:  # type: ignore[override]
        return self._connected

    async def declare_topology(self) -> None:  # type: ignore[override]
        return None

    async def close(self) -> None:  # type: ignore[override]
        return None


def test_worker_health_ok_when_connected() -> None:
    settings = Settings(app_env="test")
    app = create_worker_app(settings, _StubRabbit(True), enable_background=False)  # type: ignore[arg-type]
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_worker_health_503_when_disconnected() -> None:
    settings = Settings(app_env="test")
    app = create_worker_app(settings, _StubRabbit(False), enable_background=False)  # type: ignore[arg-type]
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
