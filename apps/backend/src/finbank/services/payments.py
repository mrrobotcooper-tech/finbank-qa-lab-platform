from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from finbank.adapters.payment import PaymentGateway
from finbank.domain.authz import assert_can_operate_money, can_read_account
from finbank.domain.enums import Currency, OperationType, PaymentStatus, PaymentType, Role
from finbank.domain.errors import AuthorizationError, ValidationError
from finbank.domain.payments import evaluate_payment, post_payment_ledger
from finbank.models.banking import Account, AuditEvent, LedgerEntry, OutboxEvent, Payment
from finbank.models.identity import User
from finbank.services.mapping import to_snapshot


class PaymentService:
    def __init__(self, session: AsyncSession, gateway: PaymentGateway) -> None:
        self._session = session
        self._gateway = gateway

    async def list_for_actor(self, actor: User) -> list[Payment]:
        stmt = select(Payment).order_by(Payment.created_at.desc()).limit(100)
        if Role(actor.role) == Role.CUSTOMER:
            stmt = stmt.where(Payment.initiator_user_id == actor.id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def get(self, payment_id: UUID, actor: User) -> Payment:
        payment = await self._session.get(Payment, payment_id)
        if payment is None:
            raise ValidationError("Payment not found")
        if Role(actor.role) == Role.CUSTOMER and payment.initiator_user_id != actor.id:
            raise AuthorizationError("Not allowed to read this payment")
        return payment

    async def create(
        self,
        *,
        actor: User,
        account_id: UUID,
        amount: int,
        currency: str,
        payment_type: str,
        payee: str,
        idempotency_key: str,
        scheduled_at: datetime | None,
        correlation_id: str,
        ip: str | None,
    ) -> Payment:
        assert_can_operate_money(Role(actor.role))
        if not idempotency_key.strip():
            raise ValidationError("Idempotency-Key is required")
        existing = await self._find_idempotent(actor.id, idempotency_key)
        if existing is not None:
            return existing
        try:
            kind = PaymentType(payment_type)
            Currency(currency)
        except ValueError as exc:
            raise ValidationError("Invalid payment type or currency") from exc

        result = await self._session.execute(
            select(Account).where(Account.id == account_id).with_for_update()
        )
        account = result.scalar_one_or_none()
        if account is None:
            raise ValidationError("Account not found")
        if not can_read_account(Role.CUSTOMER, account.user_id, actor.id):
            raise AuthorizationError("Account is not owned by the actor")

        now = datetime.now(UTC)
        decision = evaluate_payment(
            account=to_snapshot(account),
            amount=amount,
            currency=Currency(currency),
            scheduled_at=scheduled_at,
            now=now,
        )
        payment = Payment(
            id=uuid4(),
            initiator_user_id=actor.id,
            account_id=account.id,
            payment_type=kind.value,
            payee=payee.strip() or "generic-payee",
            amount=amount,
            currency=currency,
            status=decision.status.value,
            rejection_reason=decision.reason,
            idempotency_key=idempotency_key.strip(),
            scheduled_at=scheduled_at,
            correlation_id=correlation_id,
        )
        self._session.add(payment)
        if decision.status is PaymentStatus.PENDING:
            await self._settle(payment, account, correlation_id=correlation_id, ip=ip)
        else:
            self._audit(actor.id, payment, correlation_id, ip)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            replay = await self._find_idempotent(actor.id, idempotency_key)
            if replay is None:
                raise
            return replay
        await self._session.refresh(payment)
        return payment

    async def process_due_scheduled(self) -> int:
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(Payment).where(
                Payment.status == PaymentStatus.SCHEDULED.value,
                Payment.scheduled_at <= now,
            )
        )
        due = list(result.scalars())
        processed = 0
        for payment in due:
            account = await self._session.get(Account, payment.account_id)
            if account is None:
                payment.status = PaymentStatus.FAILED.value
                payment.rejection_reason = "ACCOUNT_MISSING"
                continue
            await self._settle(payment, account, correlation_id=payment.correlation_id, ip=None)
            processed += 1
        await self._session.commit()
        return processed

    async def _settle(
        self, payment: Payment, account: Account, *, correlation_id: str, ip: str | None
    ) -> None:
        payment.status = PaymentStatus.PROCESSING.value
        charge = await self._gateway.charge(
            amount=payment.amount,
            currency=payment.currency,
            reference=str(payment.id),
            payee=payment.payee,
        )
        payment.external_reference = charge.reference
        if not charge.approved:
            payment.status = PaymentStatus.REJECTED.value
            payment.rejection_reason = charge.reason
            self._audit(payment.initiator_user_id, payment, correlation_id, ip)
            return
        snapshot = to_snapshot(account)
        if payment.amount > snapshot.available_balance:
            payment.status = PaymentStatus.REJECTED.value
            payment.rejection_reason = "INSUFFICIENT_FUNDS"
            self._audit(payment.initiator_user_id, payment, correlation_id, ip)
            return
        after, posting = post_payment_ledger(account=snapshot, amount=payment.amount)
        account.available_balance = after
        payment.status = PaymentStatus.COMPLETED.value
        self._session.add(
            LedgerEntry(
                account_id=account.id,
                operation_id=payment.id,
                operation_type=OperationType.PAYMENT.value,
                direction=posting.direction.value,
                amount=payment.amount,
                currency=payment.currency,
                balance_after=after,
                description=f"Payment {payment.payee}",
            )
        )
        self._session.add(
            OutboxEvent(
                event_type="notification.payment.completed",
                payload={"user_id": str(payment.initiator_user_id), "payment_id": str(payment.id)},
            )
        )
        self._audit(payment.initiator_user_id, payment, correlation_id, ip)

    def _audit(self, actor_id: UUID, payment: Payment, correlation_id: str, ip: str | None) -> None:
        self._session.add(
            AuditEvent(
                actor_user_id=actor_id,
                action="payment.updated",
                entity_type="payment",
                entity_id=payment.id,
                before_state=None,
                after_state={"status": payment.status, "reason": payment.rejection_reason},
                correlation_id=correlation_id,
                ip=ip,
            )
        )

    async def _find_idempotent(self, user_id: UUID, key: str) -> Payment | None:
        result = await self._session.execute(
            select(Payment).where(
                Payment.initiator_user_id == user_id, Payment.idempotency_key == key.strip()
            )
        )
        return result.scalar_one_or_none()
