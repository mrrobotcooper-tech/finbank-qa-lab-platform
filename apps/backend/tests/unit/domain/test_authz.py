from uuid import uuid4

import pytest

from finbank.core.defects import enabled_defects
from finbank.domain.authz import (
    assert_can_admin,
    assert_can_operate_money,
    can_read_account,
)
from finbank.domain.enums import Role
from finbank.domain.errors import AuthorizationError


def test_only_customer_moves_money() -> None:
    assert_can_operate_money(Role.CUSTOMER)
    with pytest.raises(AuthorizationError):
        assert_can_operate_money(Role.SUPPORT)
    with pytest.raises(AuthorizationError):
        assert_can_operate_money(Role.ADMIN)


def test_aut_001_allows_staff_money_when_on() -> None:
    with enabled_defects("DEF-AUT-001"):
        assert_can_operate_money(Role.SUPPORT)
        assert_can_operate_money(Role.ADMIN)


def test_only_admin_mutates_administration() -> None:
    assert_can_admin(Role.ADMIN)
    with pytest.raises(AuthorizationError):
        assert_can_admin(Role.SUPPORT)


def test_support_can_read_foreign_accounts_customer_cannot() -> None:
    owner = uuid4()
    other = uuid4()
    assert can_read_account(Role.SUPPORT, owner, other)
    assert can_read_account(Role.CUSTOMER, owner, owner)
    assert not can_read_account(Role.CUSTOMER, owner, other)
