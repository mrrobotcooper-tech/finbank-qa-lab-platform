from __future__ import annotations

from redis.asyncio import Redis

from finbank.adapters.health import ComponentStatus
from finbank.core.config import Settings


class RedisChecker:
    name = "redis"

    def __init__(self, settings: Settings, client: Redis[str] | None = None) -> None:
        self._settings = settings
        self._client: Redis[str] = client or Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=settings.dependency_timeout_seconds,
            socket_timeout=settings.dependency_timeout_seconds,
            decode_responses=True,
        )

    async def check(self) -> ComponentStatus:
        try:
            pong = await self._client.ping()
            if pong is True:
                return ComponentStatus(name=self.name, status="up")
            return ComponentStatus(name=self.name, status="down", detail="unexpected ping reply")
        except Exception as exc:  # noqa: BLE001
            return ComponentStatus(
                name=self.name,
                status="down",
                detail=None if self._settings.app_env == "prod" else str(exc)[:240],
            )

    async def close(self) -> None:
        closer = getattr(self._client, "aclose", self._client.close)
        await closer()
