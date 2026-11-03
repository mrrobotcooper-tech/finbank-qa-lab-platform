from finbank.core.defects import defect_on
from finbank.domain.enums import Role
from finbank.domain.errors import AuthorizationError


def assert_can_operate_money(role: Role) -> None:
    if defect_on("DEF-AUT-001"):
        return
    if role != Role.CUSTOMER:
        raise AuthorizationError("Only customers can move money")


def assert_can_admin(role: Role) -> None:
    if role != Role.ADMIN:
        raise AuthorizationError("Administrator role required")


def assert_can_operate_or_read_admin(role: Role) -> None:
    if role not in {Role.ADMIN, Role.SUPPORT}:
        raise AuthorizationError("Support or administrator role required")


def assert_can_mutate_admin(role: Role) -> None:
    if role != Role.ADMIN:
        raise AuthorizationError("Administrator role required")


def can_read_account(role: Role, owner_user_id: object, actor_user_id: object) -> bool:
    if role in {Role.ADMIN, Role.SUPPORT}:
        return True
    return owner_user_id == actor_user_id
