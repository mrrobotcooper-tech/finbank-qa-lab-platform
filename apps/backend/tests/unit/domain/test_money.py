import pytest

from finbank.core.defects import enabled_defects
from finbank.domain.errors import ValidationError
from finbank.domain.money import projected_available, require_positive_amount


def test_require_positive_amount_accepts_minor_units() -> None:
    require_positive_amount(1)
    require_positive_amount(99)


@pytest.mark.parametrize("amount", [0, -1])
def test_require_positive_amount_rejects_non_positive(amount: int) -> None:
    with pytest.raises(ValidationError, match="greater than zero"):
        require_positive_amount(amount)


def test_val_001_accepts_zero_when_on() -> None:
    with enabled_defects("DEF-VAL-001"):
        require_positive_amount(0)
        require_positive_amount(-1)


def test_require_positive_amount_rejects_bool() -> None:
    with pytest.raises(ValidationError, match="integer"):
        require_positive_amount(True)  # type: ignore[arg-type]


def test_projected_available_subtracts_holds_from_ledger_net() -> None:
    assert projected_available(entries_net=10_000, held_balance=1_500) == 8_500
    assert projected_available(entries_net=0, held_balance=0) == 0
