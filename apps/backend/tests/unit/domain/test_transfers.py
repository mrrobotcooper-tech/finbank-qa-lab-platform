from uuid import uuid4

from finbank.core.defects import enabled_defects
from finbank.domain.accounts import AccountSnapshot
from finbank.domain.enums import (
    AccountStatus,
    AccountType,
    Currency,
    LedgerDirection,
    TransferStatus,
)
from finbank.domain.transfers import evaluate_transfer, post_transfer_ledger


def _account(
    *,
    balance: int = 10_000,
    status: AccountStatus = AccountStatus.ACTIVE,
    currency: Currency = Currency.ARS,
    user_id=None,
    per_op: int = 8_000,
    daily: int = 20_000,
) -> AccountSnapshot:
    return AccountSnapshot(
        id=uuid4(),
        user_id=user_id or uuid4(),
        account_number="3220000000000000000001",
        type=AccountType.CHECKING,
        currency=currency,
        status=status,
        available_balance=balance,
        held_balance=0,
        daily_transfer_limit=daily,
        per_operation_limit=per_op,
    )


def test_completes_when_funds_and_limits_allow() -> None:
    source = _account(balance=10_000)
    dest = _account(balance=1_000)
    decision = evaluate_transfer(
        source=source, destination=dest, amount=2_000, currency=Currency.ARS, daily_spent=0
    )
    assert decision.accepted
    src_after, dst_after, debit, credit = post_transfer_ledger(
        source=source, destination=dest, amount=2_000
    )
    assert src_after == 8_000
    assert dst_after == 3_000
    assert debit.direction is LedgerDirection.DEBIT
    assert credit.direction is LedgerDirection.CREDIT
    assert debit.amount == credit.amount == 2_000


def test_rejects_insufficient_funds() -> None:
    decision = evaluate_transfer(
        source=_account(balance=500),
        destination=_account(),
        amount=501,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.status is TransferStatus.REJECTED
    assert decision.reason == "INSUFFICIENT_FUNDS"


def test_rejects_blocked_source() -> None:
    decision = evaluate_transfer(
        source=_account(status=AccountStatus.BLOCKED),
        destination=_account(),
        amount=100,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.reason == "SOURCE_NOT_ACTIVE"


def test_rejects_currency_mismatch() -> None:
    decision = evaluate_transfer(
        source=_account(currency=Currency.ARS),
        destination=_account(currency=Currency.USD),
        amount=100,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.reason == "CURRENCY_MISMATCH"


def test_rejects_per_operation_limit() -> None:
    decision = evaluate_transfer(
        source=_account(balance=50_000, per_op=1_000),
        destination=_account(),
        amount=1_001,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.reason == "PER_OPERATION_LIMIT"


def test_rejects_daily_limit_including_prior_spend() -> None:
    decision = evaluate_transfer(
        source=_account(balance=50_000, daily=5_000),
        destination=_account(),
        amount=1_000,
        currency=Currency.ARS,
        daily_spent=4_500,
    )
    assert decision.reason == "DAILY_LIMIT"


def test_rejects_same_account() -> None:
    account = _account()
    decision = evaluate_transfer(
        source=account,
        destination=account,
        amount=100,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.reason == "SAME_ACCOUNT"


def test_rejected_transfer_must_not_change_balances() -> None:
    source = _account(balance=100)
    dest = _account(balance=50)
    decision = evaluate_transfer(
        source=source, destination=dest, amount=500, currency=Currency.ARS, daily_spent=0
    )
    assert not decision.accepted
    assert source.available_balance == 100
    assert dest.available_balance == 50


def test_accepts_amount_equal_to_per_operation_limit() -> None:
    decision = evaluate_transfer(
        source=_account(balance=50_000, per_op=1_000),
        destination=_account(),
        amount=1_000,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.accepted


def test_accepts_amount_equal_to_remaining_daily_limit() -> None:
    decision = evaluate_transfer(
        source=_account(balance=50_000, daily=5_000),
        destination=_account(),
        amount=500,
        currency=Currency.ARS,
        daily_spent=4_500,
    )
    assert decision.accepted


def test_rejects_destination_blocked() -> None:
    decision = evaluate_transfer(
        source=_account(),
        destination=_account(status=AccountStatus.BLOCKED),
        amount=100,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.reason == "DESTINATION_NOT_ACTIVE"


def test_rejects_non_positive_amount() -> None:
    decision = evaluate_transfer(
        source=_account(),
        destination=_account(),
        amount=0,
        currency=Currency.ARS,
        daily_spent=0,
    )
    assert decision.reason == "INVALID_AMOUNT"


def test_fun_001_accepts_nsf_when_on() -> None:
    with enabled_defects("DEF-FUN-001"):
        decision = evaluate_transfer(
            source=_account(balance=500),
            destination=_account(),
            amount=501,
            currency=Currency.ARS,
            daily_spent=0,
        )
    assert decision.accepted


def test_dat_001_credits_zero_when_on() -> None:
    source = _account(balance=10_000)
    dest = _account(balance=1_000)
    with enabled_defects("DEF-DAT-001"):
        _src_after, dst_after, debit, credit = post_transfer_ledger(
            source=source, destination=dest, amount=2_000
        )
    assert debit.amount == 2_000
    assert credit.amount == 0
    assert dst_after == 1_000
