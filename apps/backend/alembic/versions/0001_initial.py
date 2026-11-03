"""initial banking schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", postgresql.CITEXT(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(32)),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('CUSTOMER','SUPPORT','ADMIN')", name="ck_users_role"),
        sa.CheckConstraint(
            "status IN ('PENDING_VERIFICATION','ACTIVE','LOCKED','DISABLED')",
            name="ck_users_status",
        ),
    )
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("ip", sa.String(64)),
        sa.Column("user_agent", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_table(
        "password_resets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])
    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("detail", sa.Text()),
        sa.Column("ip", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("account_number", sa.String(22), nullable=False, unique=True),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("available_balance", sa.BigInteger(), nullable=False),
        sa.Column("held_balance", sa.BigInteger(), nullable=False),
        sa.Column("daily_transfer_limit", sa.BigInteger(), nullable=False),
        sa.Column("per_operation_limit", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("type IN ('CHECKING','SAVINGS')", name="ck_accounts_type"),
        sa.CheckConstraint("currency IN ('ARS','USD')", name="ck_accounts_currency"),
        sa.CheckConstraint("status IN ('ACTIVE','BLOCKED','CLOSED')", name="ck_accounts_status"),
        sa.CheckConstraint("available_balance >= 0", name="ck_accounts_available_nonneg"),
        sa.CheckConstraint("held_balance >= 0", name="ck_accounts_held_nonneg"),
    )
    op.create_index("ix_accounts_user_status", "accounts", ["user_id", "status"])
    op.create_table(
        "transfers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("initiator_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("source_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("destination_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("rejection_reason", sa.String(64)),
        sa.Column("correlation_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("initiator_user_id", "idempotency_key", name="uq_transfers_idempotency"),
        sa.CheckConstraint("status IN ('PENDING','COMPLETED','REJECTED','FAILED')", name="ck_transfers_status"),
        sa.CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
    )
    op.create_index("ix_transfers_initiator_user_id", "transfers", ["initiator_user_id"])
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("initiator_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("payment_type", sa.String(16), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False, server_default="mock-gateway"),
        sa.Column("payee", sa.String(128), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("rejection_reason", sa.String(64)),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("external_reference", sa.String(128)),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("correlation_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("initiator_user_id", "idempotency_key", name="uq_payments_idempotency"),
        sa.CheckConstraint(
            "status IN ('PENDING','PROCESSING','SCHEDULED','COMPLETED','REJECTED','FAILED')",
            name="ck_payments_status",
        ),
        sa.CheckConstraint(
            "payment_type IN ('SERVICE','CARD','INVOICE','SCHEDULED')",
            name="ck_payments_type",
        ),
        sa.CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )
    op.create_index("ix_payments_initiator_user_id", "payments", ["initiator_user_id"])
    op.create_table(
        "ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("operation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operation_type", sa.String(16), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("balance_after", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("direction IN ('DEBIT','CREDIT')", name="ck_ledger_direction"),
        sa.CheckConstraint(
            "operation_type IN ('TRANSFER','PAYMENT','FEE','ADJUSTMENT')",
            name="ck_ledger_op_type",
        ),
        sa.CheckConstraint("amount > 0", name="ck_ledger_amount_positive"),
    )
    op.create_index("ix_ledger_account_created", "ledger_entries", ["account_id", "created_at"])
    op.create_index("ix_ledger_entries_operation_id", "ledger_entries", ["operation_id"])
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("before_state", postgresql.JSONB()),
        sa.Column("after_state", postgresql.JSONB()),
        sa.Column("correlation_id", sa.String(64), nullable=False),
        sa.Column("ip", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"])
    op.create_index("ix_audit_events_correlation_id", "audit_events", ["correlation_id"])
    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_outbox_events_published_at", "outbox_events", ["published_at"])
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("channel", sa.String(16), nullable=False),
        sa.Column("template", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("channel IN ('EMAIL','SMS','IN_APP')", name="ck_notifications_channel"),
        sa.CheckConstraint("status IN ('QUEUED','SENT','FAILED')", name="ck_notifications_status"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'finbank_qa_reader') THEN
            GRANT SELECT ON ALL TABLES IN SCHEMA public TO finbank_qa_reader;
            GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO finbank_qa_reader;
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("outbox_events")
    op.drop_table("audit_events")
    op.drop_table("ledger_entries")
    op.drop_table("payments")
    op.drop_table("transfers")
    op.drop_table("accounts")
    op.drop_table("activity_logs")
    op.drop_table("password_resets")
    op.drop_table("sessions")
    op.drop_table("users")
