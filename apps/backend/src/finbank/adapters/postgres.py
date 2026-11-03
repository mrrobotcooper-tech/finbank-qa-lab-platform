from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from finbank.adapters.health import ComponentStatus
from finbank.core.config import Settings


class PostgresChecker:
    name = "postgres"

    def __init__(self, settings: Settings, engine: AsyncEngine | None = None) -> None:
        self._settings = settings
        self._engine = engine or create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def check(self) -> ComponentStatus:
        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return ComponentStatus(name=self.name, status="up")
        except Exception as exc:  # noqa: BLE001 — surface connectivity, hide secrets
            return ComponentStatus(
                name=self.name,
                status="down",
                detail=_safe_detail(exc, self._settings),
            )

    async def dispose(self) -> None:
        await self._engine.dispose()


def _safe_detail(exc: Exception, settings: Settings) -> str | None:
    if settings.app_env == "prod":
        return None
    return str(exc)[:240]
