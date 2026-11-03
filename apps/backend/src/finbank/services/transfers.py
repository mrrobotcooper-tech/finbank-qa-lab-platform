from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from finbank.core.defects import skip_audit, skip_outbox
from finbank.domain.authz import assert_can_operate_money, can_read_account
from finbank.domain.enums import Currency, OperationType, Role, TransferStatus
from finbank.domain.errors import AuthorizationError, ValidationError
from finbank.domain.transfers import evaluate_transfer, post_transfer_ledger
from finbank.models.banking import Account, AuditEvent, LedgerEntry, OutboxEvent, Transfer
from finbank.models.identity import ActivityLog, User
from finbank.services.mapping import to_snapshot


class TransferService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_actor(self, actor: User) -> list[Transfer]:
        stmt = select(Transfer).order_by(Transfer.created_at.desc()).limit(100)
        if Role(actor.role) == Role.CUSTOMER:
            stmt = stmt.where(Transfer.initiator_user_id == actor.id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def get(self, transfer_id: UUID, actor: User) -> Transfer:
        transfer = await self._session.get(Transfer, transfer_id)
        if transfer is None:
            raise ValidationError("Transfer not found")
        if Role(actor.role) == Role.CUSTOMER and transfer.initiator_user_id != actor.id:
            raise AuthorizationError("Not allowed to read this transfer")
        return transfer

    async def create(
        self,
        *,
        actor: User,
        source_account_id: UUID,
        destination_account_id: UUID | None,
        destination_account_number: str | None = None,
        amount: int,
        currency: str,
        idempotency_key: str,
        correlation_id: str,
        ip: str | None,
    ) -> Transfer:
        assert_can_operate_money(Role(actor.role))
        if not idempotency_key.strip():
            raise ValidationError("Idempotency-Key is required")
        existing = await self._find_idempotent(actor.id, idempotency_key)
        if existing is not None:
            return existing
        if destination_account_id is None:
            number = (destination_account_number or "").strip()
            if not number:
                raise ValidationError("Destination account is required")
            found = await self._session.scalar(
                select(Account.id).where(Account.account_number == number)
            )
            if found is None:
                raise ValidationError("Account not found")
            destination_account_id = found
        try:
            Currency(currency)
        except ValueError as exc:
            raise ValidationError("Invalid currency") from exc

        ids = sorted([source_account_id, destination_account_id], key=str)
        accounts = {
            account.id: account
            for account in (
                await self._session.execute(
                    select(Account).where(Account.id.in_(ids)).with_for_update()
                )
            ).scalars()
        }
        source = accounts.get(source_account_id)
        destination = accounts.get(destination_account_id)
        if source is None or destination is None:
            raise ValidationError("Account not found")
        if not can_read_account(Role.CUSTOMER, source.user_id, actor.id):
            raise AuthorizationError("Source account is not owned by the actor")

        daily_spent = await self._daily_spent(source.id)
        decision = evaluate_transfer(
            source=to_snapshot(source),
            destination=to_snapshot(destination),
            amount=amount,
            currency=Currency(currency),
            daily_spent=daily_spent,
        )
        transfer = Transfer(
            id=uuid4(),
            initiator_user_id=actor.id,
            idempotency_key=idempotency_key.strip(),
            source_account_id=source.id,
            destination_account_id=destination.id,
            amount=amount,
            currency=currency,
            status=decision.status.value,
            rejection_reason=decision.reason,
            correlation_id=correlation_id,
        )
        self._session.add(transfer)
        if decision.accepted:
            src_after, dst_after, debit, credit = post_transfer_ledger(
                source=to_snapshot(source), destination=to_snapshot(destination), amount=amount
            )
            source.available_balance = src_after
            destination.available_balance = dst_after
            transfer.completed_at = datetime.now(UTC)
            self._session.add_all(
                [
                    LedgerEntry(
                        account_id=source.id,
                        operation_id=transfer.id,
                        operation_type=OperationType.TRANSFER.value,
                        direction=debit.direction.value,
                        amount=debit.amount,
                        currency=currency,
                        balance_after=src_after,
                        description="Transfer debit",
                    ),
                    LedgerEntry(
                        account_id=destination.id,
                        operation_id=transfer.id,
                        operation_type=OperationType.TRANSFER.value,
                        direction=credit.direction.value,
                        amount=credit.amount,
                        currency=currency,
                        balance_after=dst_after,
                        description="Transfer credit",
                    ),
                ]
            )
            if not skip_outbox():
                self._session.add(
                    OutboxEvent(
                        event_type="notification.transfer.completed",
                        payload={
                            "user_id": str(actor.id),
                            "transfer_id": str(transfer.id),
                            "amount": amount,
                            "currency": currency,
                        },
                    )
                )
        if not skip_audit():
            self._session.add(
                AuditEvent(
                    actor_user_id=actor.id,
                    action="transfer.created",
                    entity_type="transfer",
                    entity_id=transfer.id,
                    before_state=None,
                    after_state={
                        "status": transfer.status,
                        "amount": amount,
                        "reason": transfer.rejection_reason,
                    },
                    correlation_id=correlation_id,
                    ip=ip,
                )
            )
        self._session.add(
            ActivityLog(
                user_id=actor.id,
                action="transfer",
                detail=transfer.status,
                ip=ip,
            )
        )
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            replay = await self._find_idempotent(actor.id, idempotency_key)
            if replay is None:
                raise
            return replay
        await self._session.refresh(transfer)
        return transfer

    async def _find_idempotent(self, user_id: UUID, key: str) -> Transfer | None:
        result = await self._session.execute(
            select(Transfer).where(
                Transfer.initiator_user_id == user_id, Transfer.idempotency_key == key.strip()
            )
        )
        return result.scalar_one_or_none()

    async def _daily_spent(self, source_account_id: UUID) -> int:
        start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self._session.execute(
            select(func.coalesce(func.sum(Transfer.amount), 0)).where(
                Transfer.source_account_id == source_account_id,
                Transfer.status == TransferStatus.COMPLETED.value,
                Transfer.created_at >= start,
            )
        )
        value = result.scalar_one()
        return int(value)
