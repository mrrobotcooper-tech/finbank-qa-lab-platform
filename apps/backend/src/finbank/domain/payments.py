from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from finbank.domain.accounts import AccountSnapshot
from finbank.domain.enums import Currency, LedgerDirection, PaymentStatus
from finbank.domain.money import require_positive_amount
from finbank.domain.transfers import LedgerPosting


@dataclass(frozen=True)
class PaymentDecision:
    status: PaymentStatus
    reason: str | None = None


def evaluate_payment(
    *,
    account: AccountSnapshot,
    amount: int,
    currency: Currency,
    scheduled_at: datetime | None,
    now: datetime,
) -> PaymentDecision:
    try:
        require_positive_amount(amount)
    except Exception:
        return PaymentDecision(PaymentStatus.REJECTED, "INVALID_AMOUNT")
    if not account.can_originate:
        return PaymentDecision(PaymentStatus.REJECTED, "SOURCE_NOT_ACTIVE")
    if account.currency != currency:
        return PaymentDecision(PaymentStatus.REJECTED, "CURRENCY_MISMATCH")
    if scheduled_at is not None and scheduled_at > now:
        return PaymentDecision(PaymentStatus.SCHEDULED)
    if amount > account.available_balance:
        return PaymentDecision(PaymentStatus.REJECTED, "INSUFFICIENT_FUNDS")
    return PaymentDecision(PaymentStatus.PENDING)


def post_payment_ledger(*, account: AccountSnapshot, amount: int) -> tuple[int, LedgerPosting]:
    available_after = account.available_balance - amount
    posting = LedgerPosting(
        account_id=account.id,
        direction=LedgerDirection.DEBIT,
        amount=amount,
        currency=account.currency,
        balance_after=available_after,
    )
    return available_after, posting
