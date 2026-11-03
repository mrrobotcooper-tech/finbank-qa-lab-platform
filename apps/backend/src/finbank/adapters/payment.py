from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx
import structlog

from finbank.core.config import Settings

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ChargeResult:
    approved: bool
    reference: str
    reason: str | None = None


class PaymentGateway(Protocol):
    async def charge(
        self, *, amount: int, currency: str, reference: str, payee: str
    ) -> ChargeResult: ...


class HttpPaymentGateway:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client or httpx.AsyncClient(
            base_url=settings.payment_gateway_url,
            timeout=settings.dependency_timeout_seconds,
        )

    async def charge(
        self, *, amount: int, currency: str, reference: str, payee: str
    ) -> ChargeResult:
        try:
            response = await self._client.post(
                "/charges",
                json={
                    "amount": amount,
                    "currency": currency,
                    "reference": reference,
                    "payee": payee,
                },
            )
            response.raise_for_status()
            body = response.json()
            approved = body.get("status") == "approved"
            return ChargeResult(
                approved=approved,
                reference=str(body.get("reference", reference)),
                reason=None if approved else str(body.get("reason", "GATEWAY_REJECTED")),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("payment_gateway_error", error=str(exc)[:200])
            return ChargeResult(approved=False, reference=reference, reason="GATEWAY_UNAVAILABLE")


class FakePaymentGateway:
    def __init__(self, *, approve: bool = True) -> None:
        self.approve = approve
        self.calls: list[dict[str, object]] = []

    async def charge(
        self, *, amount: int, currency: str, reference: str, payee: str
    ) -> ChargeResult:
        self.calls.append(
            {"amount": amount, "currency": currency, "reference": reference, "payee": payee}
        )
        if not self.approve or payee.upper() == "REJECT":
            return ChargeResult(approved=False, reference=reference, reason="GATEWAY_REJECTED")
        return ChargeResult(approved=True, reference=reference)
