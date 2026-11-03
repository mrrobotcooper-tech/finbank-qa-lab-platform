from finbank.domain.accounts import AccountSnapshot
from finbank.domain.enums import AccountStatus, AccountType, Currency
from finbank.models.banking import Account

DEFAULT_PER_OPERATION = 5_000_000
DEFAULT_DAILY = 20_000_000


def to_snapshot(account: Account) -> AccountSnapshot:
    return AccountSnapshot(
        id=account.id,
        user_id=account.user_id,
        account_number=account.account_number,
        type=AccountType(account.type),
        currency=Currency(account.currency),
        status=AccountStatus(account.status),
        available_balance=account.available_balance,
        held_balance=account.held_balance,
        daily_transfer_limit=account.daily_transfer_limit,
        per_operation_limit=account.per_operation_limit,
    )
