import pytest

from finbank.core.defects import (
    bind_request_defects,
    configure_startup_defects,
    defect_on,
    enabled_defects,
    is_defect_active,
    reset_request_defects,
    resolve_active_defects,
    skip_audit,
    skip_outbox,
)


def test_defects_are_ignored_outside_lab_environments() -> None:
    active = resolve_active_defects("dev", "DEF-001,DEF-002")
    assert active == frozenset()
    assert not is_defect_active(active, "DEF-001")


def test_defects_are_ignored_in_prod_even_if_requested() -> None:
    assert resolve_active_defects("prod", "DEF-001") == frozenset()


def test_defects_enable_in_test_env() -> None:
    active = resolve_active_defects("test", "DEF-001, DEF-002")
    assert active == frozenset({"DEF-001", "DEF-002"})
    assert is_defect_active(active, "DEF-001")
    assert not is_defect_active(active, "DEF-999")


def test_empty_flags_are_noop() -> None:
    assert resolve_active_defects("ci", "") == frozenset()
    assert resolve_active_defects("ci", "  ,  ") == frozenset()


def test_header_flags_enable_only_in_lab_env() -> None:
    ignored = bind_request_defects("dev", "DEF-FUN-001")
    try:
        assert not defect_on("DEF-FUN-001")
    finally:
        reset_request_defects(ignored)
    token = bind_request_defects("test", "DEF-FUN-001")
    try:
        assert defect_on("DEF-FUN-001")
    finally:
        reset_request_defects(token)


def test_outbox_is_written_when_lab_off() -> None:
    assert not skip_outbox()


def test_audit_is_written_when_lab_off() -> None:
    assert not skip_audit()


def test_rel_and_aud_defects_skip_side_effects() -> None:
    with enabled_defects("DEF-REL-001", "DEF-AUD-001"):
        assert skip_outbox()
        assert skip_audit()
    assert not skip_outbox()
    assert not skip_audit()


def test_env_flags_require_lab_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("FINBANK_DEFECTS", "DEF-FUN-001")
    assert defect_on("DEF-FUN-001")
    monkeypatch.setenv("APP_ENV", "dev")
    assert not defect_on("DEF-FUN-001")


def test_startup_defects_reset_between_configs() -> None:
    configure_startup_defects("test", "DEF-SEC-001")
    try:
        assert defect_on("DEF-SEC-001")
    finally:
        configure_startup_defects("test", "")
    assert not defect_on("DEF-SEC-001")
