from __future__ import annotations

import secrets

BANK_PREFIX = "322000"


def generate_account_number() -> str:
    """22-digit fictitious CBU-like number. Not a real CBU."""
    body = "".join(str(secrets.randbelow(10)) for _ in range(16))
    return f"{BANK_PREFIX}{body}"
