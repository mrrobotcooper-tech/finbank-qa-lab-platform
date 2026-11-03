from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finbank.domain.authz import can_read_account
from finbank.domain.enums import Role
from finbank.domain.errors import AuthorizationError, ValidationError
from finbank.models.banking import Account, LedgerEntry
from finbank.models.identity import User


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_actor(self, actor: User) -> list[Account]:
        stmt = select(Account).order_by(Account.account_number.asc())
        if Role(actor.role) == Role.CUSTOMER:
            stmt = stmt.where(Account.user_id == actor.id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def get(self, account_id: UUID, actor: User) -> Account:
        account = await self._session.get(Account, account_id)
        if account is None:
            raise ValidationError("Account not found")
        if not can_read_account(Role(actor.role), account.user_id, actor.id):
            raise AuthorizationError("Not allowed to read this account")
        return account

    async def movements(self, account_id: UUID, actor: User) -> list[LedgerEntry]:
        await self.get(account_id, actor)
        result = await self._session.execute(
            select(LedgerEntry)
            .where(LedgerEntry.account_id == account_id)
            .order_by(LedgerEntry.created_at.desc())
            .limit(100)
        )
        return list(result.scalars())
