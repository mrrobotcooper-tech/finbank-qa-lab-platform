import pytest

from finbank.adapters.payment import FakePaymentGateway


@pytest.mark.asyncio
async def test_fake_gateway_approves_by_default() -> None:
    gateway = FakePaymentGateway()
    result = await gateway.charge(amount=100, currency="ARS", reference="r1", payee="AYSA")
    assert result.approved is True
    assert result.reason is None


@pytest.mark.asyncio
async def test_fake_gateway_rejects_named_payee() -> None:
    gateway = FakePaymentGateway()
    result = await gateway.charge(amount=100, currency="ARS", reference="r2", payee="REJECT")
    assert result.approved is False
    assert result.reason == "GATEWAY_REJECTED"
