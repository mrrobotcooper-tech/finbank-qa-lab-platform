import pytest

from finbank.domain.errors import ValidationError
from finbank.domain.password import validate_password


def test_accepts_strong_password() -> None:
    validate_password("CorrectHorse1")


def test_rejects_short_password() -> None:
    with pytest.raises(ValidationError, match="at least 10"):
        validate_password("Ab1")


@pytest.mark.parametrize(
    ("password", "fragment"),
    [
        ("alllowercase1", "uppercase"),
        ("ALLUPPERCASE1", "lowercase"),
        ("NoDigitsHere", "digit"),
    ],
)
def test_rejects_missing_character_classes(password: str, fragment: str) -> None:
    with pytest.raises(ValidationError, match=fragment):
        validate_password(password)


def test_rejects_email_local_part() -> None:
    with pytest.raises(ValidationError, match="email"):
        validate_password("AnaPersona1", email="ana@finbank.test")
