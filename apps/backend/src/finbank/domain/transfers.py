from __future__ import annotations

from dataclasses import dataclass

from finbank.core.defects import defect_on
from finbank.domain.accounts import AccountSnapshot
from finbank.domain.enums import Currency, LedgerDirection, TransferStatus
from finbank.domain.money import require_positive_amount


@dataclass(frozen=True)
class TransferDecision:
    status: TransferStatus
    reason: str | None = None

    @property
    def accepted(self) -> bool:
        return self.status == TransferStatus.COMPLETED


@dataclass(frozen=True)
class LedgerPosting:
    account_id: object
    direction: LedgerDirection
    amount: int
    currency: Currency
    balance_after: int


def evaluate_transfer(
    *,
    source: AccountSnapshot,
    destination: AccountSnapshot,
    amount: int,
    currency: Currency,
    daily_spent: int,
) -> TransferDecision:
    try:
        require_positive_amount(amount)
    except Exception:
        return TransferDecision(TransferStatus.REJECTED, "INVALID_AMOUNT")
    if source.id == destination.id:
        return TransferDecision(TransferStatus.REJECTED, "SAME_ACCOUNT")
    if not source.can_originate:
        return TransferDecision(TransferStatus.REJECTED, "SOURCE_NOT_ACTIVE")
    if not destination.can_receive:
        return TransferDecision(TransferStatus.REJECTED, "DESTINATION_NOT_ACTIVE")
    if source.currency != destination.currency or source.currency != currency:
        return TransferDecision(TransferStatus.REJECTED, "CURRENCY_MISMATCH")
    if amount > source.available_balance and not defect_on("DEF-FUN-001"):
        return TransferDecision(TransferStatus.REJECTED, "INSUFFICIENT_FUNDS")
    if amount > source.per_operation_limit:
        return TransferDecision(TransferStatus.REJECTED, "PER_OPERATION_LIMIT")
    if daily_spent + amount > source.daily_transfer_limit:
        return TransferDecision(TransferStatus.REJECTED, "DAILY_LIMIT")
    return TransferDecision(TransferStatus.COMPLETED)


def post_transfer_ledger(
    *,
    source: AccountSnapshot,
    destination: AccountSnapshot,
    amount: int,
) -> tuple[int, int, LedgerPosting, LedgerPosting]:
    source_after = source.available_balance - amount
    credit_amount = 0 if defect_on("DEF-DAT-001") else amount
    dest_after = destination.available_balance + credit_amount
    debit = LedgerPosting(
        account_id=source.id,
        direction=LedgerDirection.DEBIT,
        amount=amount,
        currency=source.currency,
        balance_after=source_after,
    )
    credit = LedgerPosting(
        account_id=destination.id,
        direction=LedgerDirection.CREDIT,
        amount=credit_amount,
        currency=destination.currency,
        balance_after=dest_after,
    )
    return source_after, dest_after, debit, credit
