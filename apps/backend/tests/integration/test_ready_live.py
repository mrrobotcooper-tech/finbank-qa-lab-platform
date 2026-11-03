"""Live readiness against Compose. Opt-in: FINBANK_INTEGRATION=1."""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.integration

LIVE_API = os.environ.get("FINBANK_API_URL", "http://127.0.0.1:8000")


def _enabled() -> bool:
    return os.environ.get("FINBANK_INTEGRATION") == "1"


@pytest.mark.skipif(not _enabled(), reason="Set FINBANK_INTEGRATION=1 against a running stack")
def test_live_liveness() -> None:
    response = httpx.get(f"{LIVE_API}/health", timeout=5.0)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.skipif(not _enabled(), reason="Set FINBANK_INTEGRATION=1 against a running stack")
def test_live_readiness_requires_all_dependencies() -> None:
    response = httpx.get(f"{LIVE_API}/ready", timeout=5.0)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ok"
    names = {item["name"] for item in body["components"]}
    assert names == {"postgres", "redis", "rabbitmq"}
    assert all(item["status"] == "up" for item in body["components"])
