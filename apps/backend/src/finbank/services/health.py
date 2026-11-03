from __future__ import annotations

from collections.abc import Sequence

from finbank.adapters.health import ComponentStatus, DependencyChecker
from finbank.core.metrics import set_dependency_up


class HealthService:
    def __init__(self, checkers: Sequence[DependencyChecker]) -> None:
        if not checkers:
            raise ValueError("HealthService requires at least one dependency checker")
        self._checkers = list(checkers)

    async def readiness(self) -> tuple[str, list[ComponentStatus]]:
        components = [await checker.check() for checker in self._checkers]
        for component in components:
            set_dependency_up(component.name, component.status == "up")
        status = "ok" if all(item.status == "up" for item in components) else "degraded"
        return status, components
