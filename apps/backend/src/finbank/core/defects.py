from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import cast

import structlog

from finbank.core.config import AppEnv

_ALLOWED_ENVS: frozenset[str] = frozenset({"test", "ci"})
DEFECT_HEADER = "X-Finbank-Defects"

logger = structlog.get_logger(__name__)

_startup_defects: frozenset[str] = frozenset()
_request_defects: ContextVar[frozenset[str]] = ContextVar("request_defects", default=frozenset())


def resolve_active_defects(app_env: AppEnv, raw_flags: str) -> frozenset[str]:
    """Return enabled defect IDs. Fail-closed outside test/ci (ADR-0007)."""
    requested = frozenset(flag.strip() for flag in raw_flags.split(",") if flag.strip())
    if not requested:
        return frozenset()
    if app_env not in _ALLOWED_ENVS:
        logger.error(
            "defect_flags_rejected",
            app_env=app_env,
            requested=sorted(requested),
        )
        return frozenset()
    logger.warning("defect_flags_enabled", app_env=app_env, defects=sorted(requested))
    return requested


def configure_startup_defects(app_env: AppEnv, raw_flags: str) -> frozenset[str]:
    global _startup_defects
    _startup_defects = resolve_active_defects(app_env, raw_flags)
    return _startup_defects


def bind_request_defects(app_env: AppEnv, raw_flags: str) -> Token[frozenset[str]]:
    extra = resolve_active_defects(app_env, raw_flags)
    return _request_defects.set(extra)


def reset_request_defects(token: Token[frozenset[str]]) -> None:
    _request_defects.reset(token)


def current_defects() -> frozenset[str]:
    env_name = os.getenv("APP_ENV", "dev")
    env_flags = os.getenv("FINBANK_DEFECTS", "")
    from_env = resolve_active_defects(cast(AppEnv, env_name), env_flags)
    return from_env | _startup_defects | _request_defects.get()


def is_defect_active(active: frozenset[str], defect_id: str) -> bool:
    return defect_id in active


def defect_on(defect_id: str) -> bool:
    return defect_id in current_defects()


def skip_outbox() -> bool:
    return defect_on("DEF-REL-001")


def skip_audit() -> bool:
    return defect_on("DEF-AUD-001")


@contextmanager
def enabled_defects(*defect_ids: str) -> Iterator[None]:
    token = _request_defects.set(frozenset(defect_ids))
    try:
        yield
    finally:
        _request_defects.reset(token)
