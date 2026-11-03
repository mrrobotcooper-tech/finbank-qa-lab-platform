from datetime import UTC, datetime, timedelta
from uuid import uuid4

from finbank.domain.accounts import AccountSnapshot
from finbank.domain.enums import AccountStatus, AccountType, Currency, PaymentStatus
from finbank.domain.payments import evaluate_payment, post_payment_ledger

NOW = datetime(2026, 11, 3, tzinfo=UTC)


def _account(balance: int = 5_000, status: AccountStatus = AccountStatus.ACTIVE) -> AccountSnapshot:
    return AccountSnapshot(
        id=uuid4(),
        user_id=uuid4(),
        account_number="3220000000000000000002",
        type=AccountType.CHECKING,
        currency=Currency.ARS,
        status=status,
        available_balance=balance,
        held_balance=0,
        daily_transfer_limit=20_000,
        per_operation_limit=8_000,
    )


def test_instant_payment_pending_when_funds_ok() -> None:
    decision = evaluate_payment(
        account=_account(), amount=1_000, currency=Currency.ARS, scheduled_at=None, now=NOW
    )
    assert decision.status is PaymentStatus.PENDING


def test_future_schedule_does_not_require_immediate_funds() -> None:
    decision = evaluate_payment(
        account=_account(balance=1),
        amount=5_000,
        currency=Currency.ARS,
        scheduled_at=NOW + timedelta(days=1),
        now=NOW,
    )
    assert decision.status is PaymentStatus.SCHEDULED


def test_rejected_gateway_path_does_not_post_until_charged() -> None:
    account = _account()
    decision = evaluate_payment(
        account=account, amount=100, currency=Currency.ARS, scheduled_at=None, now=NOW
    )
    assert decision.status is PaymentStatus.PENDING
    assert account.available_balance == 5_000


def test_completed_payment_posts_single_debit() -> None:
    account = _account(balance=5_000)
    after, posting = post_payment_ledger(account=account, amount=1_200)
    assert after == 3_800
    assert posting.direction.value == "DEBIT"


def test_blocked_account_cannot_pay() -> None:
    decision = evaluate_payment(
        account=_account(status=AccountStatus.BLOCKED),
        amount=100,
        currency=Currency.ARS,
        scheduled_at=None,
        now=NOW,
    )
    assert decision.reason == "SOURCE_NOT_ACTIVE"
