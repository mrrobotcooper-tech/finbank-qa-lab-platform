from finbank.adapters.health import ComponentStatus


class FakeChecker:
    def __init__(self, name: str, status: str = "up", detail: str | None = None) -> None:
        self.name = name
        self._status = status
        self._detail = detail

    async def check(self) -> ComponentStatus:
        return ComponentStatus(
            name=self.name,
            status=self._status,  # type: ignore[arg-type]
            detail=self._detail,
        )
