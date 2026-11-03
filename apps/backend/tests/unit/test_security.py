from uuid import uuid4

import pytest

from finbank.core.defects import enabled_defects
from finbank.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from finbank.domain.errors import AuthenticationError

SECRET = "unit-test-jwt-secret"


def test_access_token_roundtrip() -> None:
    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        role="CUSTOMER",
        email="qa@finbank.test",
        secret=SECRET,
        ttl_seconds=60,
    )
    payload = decode_access_token(token, SECRET)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "CUSTOMER"


def test_password_hash_is_argon2_and_not_plaintext() -> None:
    raw = "Customer1!"
    hashed = hash_password(raw)
    assert hashed.startswith("$argon2")
    assert raw not in hashed
    assert verify_password(raw, hashed)


def test_verify_password_rejects_mismatch() -> None:
    hashed = hash_password("Customer1!")
    assert not verify_password("wrong-password", hashed)


def test_sec_001_accepts_mismatch_when_on() -> None:
    hashed = hash_password("Customer1!")
    with enabled_defects("DEF-SEC-001"):
        assert verify_password("wrong-password", hashed)


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(
        user_id=uuid4(),
        role="CUSTOMER",
        email="qa@finbank.test",
        secret=SECRET,
        ttl_seconds=-1,
    )
    with pytest.raises(AuthenticationError, match="Invalid or expired"):
        decode_access_token(token, SECRET)
