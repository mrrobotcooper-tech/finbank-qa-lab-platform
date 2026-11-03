from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finbank.models.base import Base

if TYPE_CHECKING:
    from finbank.models.identity import User


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("type IN ('CHECKING','SAVINGS')", name="ck_accounts_type"),
        CheckConstraint("currency IN ('ARS','USD')", name="ck_accounts_currency"),
        CheckConstraint("status IN ('ACTIVE','BLOCKED','CLOSED')", name="ck_accounts_status"),
        CheckConstraint("available_balance >= 0", name="ck_accounts_available_nonneg"),
        CheckConstraint("held_balance >= 0", name="ck_accounts_held_nonneg"),
        Index("ix_accounts_user_status", "user_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    account_number: Mapped[str] = mapped_column(String(22), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    available_balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    held_balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    daily_transfer_limit: Mapped[int] = mapped_column(BigInteger, nullable=False)
    per_operation_limit: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="accounts")


class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = (
        UniqueConstraint("initiator_user_id", "idempotency_key", name="uq_transfers_idempotency"),
        CheckConstraint(
            "status IN ('PENDING','COMPLETED','REJECTED','FAILED')",
            name="ck_transfers_status",
        ),
        CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    initiator_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    source_account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    destination_account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(64))
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("initiator_user_id", "idempotency_key", name="uq_payments_idempotency"),
        CheckConstraint(
            "status IN ('PENDING','PROCESSING','SCHEDULED','COMPLETED','REJECTED','FAILED')",
            name="ck_payments_status",
        ),
        CheckConstraint(
            "payment_type IN ('SERVICE','CARD','INVOICE','SCHEDULED')",
            name="ck_payments_type",
        ),
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    initiator_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    payment_type: Mapped[str] = mapped_column(String(16), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="mock-gateway")
    payee: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(64))
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(128))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint("direction IN ('DEBIT','CREDIT')", name="ck_ledger_direction"),
        CheckConstraint(
            "operation_type IN ('TRANSFER','PAYMENT','FEE','ADJUSTMENT')",
            name="ck_ledger_op_type",
        ),
        CheckConstraint("amount > 0", name="ck_ledger_amount_positive"),
        Index("ix_ledger_account_created", "account_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    operation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(String(16), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    before_state: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    after_state: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("channel IN ('EMAIL','SMS','IN_APP')", name="ck_notifications_channel"),
        CheckConstraint("status IN ('QUEUED','SENT','FAILED')", name="ck_notifications_status"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    template: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="QUEUED")
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
