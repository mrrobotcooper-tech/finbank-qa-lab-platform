from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from finbank.domain.enums import UserStatus


@dataclass(frozen=True)
class LockoutState:
    failed_attempts: int
    status: UserStatus
    locked_until: datetime | None


def is_currently_locked(status: UserStatus, locked_until: datetime | None, now: datetime) -> bool:
    if status == UserStatus.DISABLED:
        return True
    if locked_until is not None and locked_until > now:
        return True
    return status == UserStatus.LOCKED and (locked_until is None or locked_until > now)


def register_failed_login(
    *,
    failed_attempts: int,
    max_attempts: int,
    now: datetime,
    lockout_seconds: int,
    status: UserStatus,
) -> LockoutState:
    attempts = failed_attempts + 1
    if attempts >= max_attempts:
        return LockoutState(
            failed_attempts=attempts,
            status=UserStatus.LOCKED,
            locked_until=now + timedelta(seconds=lockout_seconds),
        )
    return LockoutState(failed_attempts=attempts, status=status, locked_until=None)


def register_successful_login(now: datetime, locked_until: datetime | None) -> LockoutState | None:
    if locked_until is not None and locked_until > now:
        return None
    return LockoutState(failed_attempts=0, status=UserStatus.ACTIVE, locked_until=None)
