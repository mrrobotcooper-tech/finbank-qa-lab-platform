from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from tests.fakes import FakeChecker

from finbank.adapters.health import DependencyChecker
from finbank.core.config import Settings
from finbank.main import create_app
from finbank.services.health import HealthService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        app_env="test",
        app_name="finbank",
        public_web_url="http://localhost:5173",
        postgres_host="localhost",
        redis_host="localhost",
        rabbitmq_host="localhost",
        finbank_defects="",
    )


@pytest.fixture
def healthy_checkers() -> list[DependencyChecker]:
    return [
        FakeChecker("postgres"),
        FakeChecker("redis"),
        FakeChecker("rabbitmq"),
    ]


@pytest.fixture
def client(settings: Settings, healthy_checkers: list[DependencyChecker]) -> TestClient:
    app = create_app(settings, health_service=HealthService(healthy_checkers))
    with TestClient(app) as test_client:
        yield test_client
