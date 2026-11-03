from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

ComponentState = Literal["up", "down"]


@dataclass(frozen=True)
class ComponentStatus:
    name: str
    status: ComponentState
    detail: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"name": self.name, "status": self.status}
        if self.detail:
            payload["detail"] = self.detail
        return payload


class DependencyChecker(Protocol):
    name: str

    async def check(self) -> ComponentStatus: ...
