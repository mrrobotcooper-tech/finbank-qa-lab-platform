from __future__ import annotations

import re

from finbank.domain.errors import ValidationError

_UPPER = re.compile(r"[A-Z]")
_LOWER = re.compile(r"[a-z]")
_DIGIT = re.compile(r"\d")
MIN_LENGTH = 10


def validate_password(password: str, *, email: str | None = None) -> None:
    if len(password) < MIN_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_LENGTH} characters")
    if _UPPER.search(password) is None:
        raise ValidationError("Password must include an uppercase letter")
    if _LOWER.search(password) is None:
        raise ValidationError("Password must include a lowercase letter")
    if _DIGIT.search(password) is None:
        raise ValidationError("Password must include a digit")
    if email:
        local = email.split("@", 1)[0].lower()
        if local and local in password.lower():
            raise ValidationError("Password must not contain the email local part")
