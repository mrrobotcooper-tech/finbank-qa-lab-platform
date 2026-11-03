from datetime import UTC, datetime, timedelta

from finbank.domain.enums import UserStatus
from finbank.domain.lockout import (
    is_currently_locked,
    register_failed_login,
    register_successful_login,
)

NOW = datetime(2026, 11, 3, 15, 0, tzinfo=UTC)


def test_locks_after_max_attempts() -> None:
    state = register_failed_login(
        failed_attempts=4,
        max_attempts=5,
        now=NOW,
        lockout_seconds=900,
        status=UserStatus.ACTIVE,
    )
    assert state.status == UserStatus.LOCKED
    assert state.locked_until == NOW + timedelta(seconds=900)
    assert is_currently_locked(state.status, state.locked_until, NOW)


def test_does_not_lock_before_threshold() -> None:
    state = register_failed_login(
        failed_attempts=1,
        max_attempts=5,
        now=NOW,
        lockout_seconds=900,
        status=UserStatus.ACTIVE,
    )
    assert state.status == UserStatus.ACTIVE
    assert state.failed_attempts == 2
    assert not is_currently_locked(state.status, state.locked_until, NOW)


def test_successful_login_clears_lock_after_expiry() -> None:
    expired = NOW - timedelta(seconds=1)
    cleared = register_successful_login(NOW, expired)
    assert cleared is not None
    assert cleared.failed_attempts == 0
    assert cleared.status == UserStatus.ACTIVE


def test_successful_login_blocked_while_lock_active() -> None:
    assert register_successful_login(NOW, NOW + timedelta(minutes=5)) is None


def test_disabled_user_is_always_blocked() -> None:
    assert is_currently_locked(UserStatus.DISABLED, None, NOW)
