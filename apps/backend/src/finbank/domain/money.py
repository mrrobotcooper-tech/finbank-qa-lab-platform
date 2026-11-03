from finbank.core.defects import defect_on
from finbank.domain.errors import ValidationError


def require_positive_amount(amount: int) -> None:
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise ValidationError("Amount must be an integer number of minor units")
    if amount <= 0 and not defect_on("DEF-VAL-001"):
        raise ValidationError("Amount must be greater than zero")


def projected_available(entries_net: int, held_balance: int) -> int:
    """Ledger net (credits - debits) minus holds equals cached available balance."""
    return entries_net - held_balance
