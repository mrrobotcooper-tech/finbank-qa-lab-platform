import pytest
from tests.fakes import FakeChecker

from finbank.services.health import HealthService


@pytest.mark.asyncio
async def test_readiness_ok_when_all_dependencies_up() -> None:
    service = HealthService(
        [FakeChecker("postgres"), FakeChecker("redis"), FakeChecker("rabbitmq")]
    )
    status, components = await service.readiness()
    assert status == "ok"
    assert [item.name for item in components] == ["postgres", "redis", "rabbitmq"]
    assert all(item.status == "up" for item in components)


@pytest.mark.asyncio
async def test_readiness_degraded_when_redis_is_down() -> None:
    service = HealthService(
        [
            FakeChecker("postgres"),
            FakeChecker("redis", status="down", detail="connection refused"),
            FakeChecker("rabbitmq"),
        ]
    )
    status, components = await service.readiness()
    assert status == "degraded"
    redis = next(item for item in components if item.name == "redis")
    assert redis.status == "down"
    assert redis.detail == "connection refused"


def test_health_service_rejects_empty_checker_list() -> None:
    with pytest.raises(ValueError, match="at least one"):
        HealthService([])
