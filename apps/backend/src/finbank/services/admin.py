from __future__ import annotations

from typing import TypedDict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from finbank.domain.authz import assert_can_mutate_admin, assert_can_operate_or_read_admin
from finbank.domain.enums import AccountStatus, Role, TransferStatus, UserStatus
from finbank.domain.errors import ValidationError
from finbank.models.banking import Account, AuditEvent, Payment, Transfer
from finbank.models.identity import User


class AdminOperations(TypedDict):
    transfers: list[Transfer]
    payments: list[Payment]


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_users(self, actor: User) -> list[User]:
        assert_can_operate_or_read_admin(Role(actor.role))
        result = await self._session.execute(select(User).order_by(User.created_at.asc()))
        return list(result.scalars())

    async def update_user(
        self,
        actor: User,
        user_id: UUID,
        *,
        status: str | None,
        role: str | None,
        correlation_id: str,
        ip: str | None,
    ) -> User:
        assert_can_mutate_admin(Role(actor.role))
        user = await self._session.get(User, user_id)
        if user is None:
            raise ValidationError("User not found")
        before = {"status": user.status, "role": user.role}
        if status is not None:
            try:
                UserStatus(status)
            except ValueError as exc:
                raise ValidationError("Invalid user status") from exc
            user.status = status
        if role is not None:
            try:
                Role(role)
            except ValueError as exc:
                raise ValidationError("Invalid role") from exc
            user.role = role
        self._session.add(
            AuditEvent(
                actor_user_id=actor.id,
                action="admin.user.updated",
                entity_type="user",
                entity_id=user.id,
                before_state=before,
                after_state={"status": user.status, "role": user.role},
                correlation_id=correlation_id,
                ip=ip,
            )
        )
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def update_account_status(
        self,
        actor: User,
        account_id: UUID,
        status: str,
        *,
        correlation_id: str,
        ip: str | None,
    ) -> Account:
        assert_can_mutate_admin(Role(actor.role))
        try:
            AccountStatus(status)
        except ValueError as exc:
            raise ValidationError("Invalid account status") from exc
        account = await self._session.get(Account, account_id)
        if account is None:
            raise ValidationError("Account not found")
        before = {"status": account.status}
        account.status = status
        self._session.add(
            AuditEvent(
                actor_user_id=actor.id,
                action="admin.account.updated",
                entity_type="account",
                entity_id=account.id,
                before_state=before,
                after_state={"status": account.status},
                correlation_id=correlation_id,
                ip=ip,
            )
        )
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def operations(self, actor: User) -> AdminOperations:
        assert_can_operate_or_read_admin(Role(actor.role))
        transfers = list(
            (
                await self._session.execute(
                    select(Transfer).order_by(Transfer.created_at.desc()).limit(50)
                )
            ).scalars()
        )
        payments = list(
            (
                await self._session.execute(
                    select(Payment).order_by(Payment.created_at.desc()).limit(50)
                )
            ).scalars()
        )
        return {"transfers": transfers, "payments": payments}

    async def indicators(self, actor: User) -> dict[str, int]:
        assert_can_operate_or_read_admin(Role(actor.role))
        users = int((await self._session.execute(select(func.count(User.id)))).scalar_one())
        accounts = int((await self._session.execute(select(func.count(Account.id)))).scalar_one())
        completed = int(
            (
                await self._session.execute(
                    select(func.count(Transfer.id)).where(
                        Transfer.status == TransferStatus.COMPLETED.value
                    )
                )
            ).scalar_one()
        )
        return {"users": users, "accounts": accounts, "completed_transfers": completed}

    async def operation_trace(self, actor: User, transfer_id: UUID) -> dict[str, object]:
        """Reduced operational view — not the full audit log (FR-AUD-004)."""
        assert_can_operate_or_read_admin(Role(actor.role))
        transfer = await self._session.get(Transfer, transfer_id)
        if transfer is None:
            raise ValidationError("Transfer not found")
        return {
            "id": str(transfer.id),
            "status": transfer.status,
            "amount": transfer.amount,
            "currency": transfer.currency,
            "correlation_id": transfer.correlation_id,
            "created_at": transfer.created_at.isoformat() if transfer.created_at else None,
        }
