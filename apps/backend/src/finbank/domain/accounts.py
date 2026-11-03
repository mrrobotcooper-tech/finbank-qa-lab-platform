from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from finbank.domain.enums import AccountStatus, AccountType, Currency


@dataclass(frozen=True)
class AccountSnapshot:
    id: UUID
    user_id: UUID
    account_number: str
    type: AccountType
    currency: Currency
    status: AccountStatus
    available_balance: int
    held_balance: int
    daily_transfer_limit: int
    per_operation_limit: int

    @property
    def can_originate(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    @property
    def can_receive(self) -> bool:
        return self.status == AccountStatus.ACTIVE
