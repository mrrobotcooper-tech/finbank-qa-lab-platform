from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from finbank.core.config import Settings
from finbank.core.security import (
    create_access_token,
    hash_password,
    hash_token,
    new_refresh_token,
    verify_password,
)
from finbank.domain.account_numbers import generate_account_number
from finbank.domain.enums import AccountType, Currency, Role, UserStatus
from finbank.domain.errors import AuthenticationError, ConflictError, ValidationError
from finbank.domain.lockout import (
    is_currently_locked,
    register_failed_login,
    register_successful_login,
)
from finbank.domain.password import validate_password
from finbank.models.banking import Account, AuditEvent, Notification, OutboxEvent
from finbank.models.identity import ActivityLog, PasswordReset, Session, User
from finbank.services.mapping import DEFAULT_DAILY, DEFAULT_PER_OPERATION


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    user: User


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings

    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        phone: str | None,
        correlation_id: str,
        ip: str | None,
    ) -> User:
        email_norm = email.strip().lower()
        if not full_name.strip():
            raise ValidationError("Full name is required")
        validate_password(password, email=email_norm)
        user = User(
            id=uuid4(),
            email=email_norm,
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            phone=phone,
            role=Role.CUSTOMER.value,
            status=UserStatus.ACTIVE.value,
        )
        account = Account(
            user_id=user.id,
            account_number=generate_account_number(),
            type=AccountType.CHECKING.value,
            currency=Currency.ARS.value,
            status="ACTIVE",
            available_balance=0,
            held_balance=0,
            daily_transfer_limit=DEFAULT_DAILY,
            per_operation_limit=DEFAULT_PER_OPERATION,
        )
        self._session.add_all([user, account])
        try:
            await self._session.flush()
            await self._audit(
                actor=user.id,
                action="user.registered",
                entity_type="user",
                entity_id=user.id,
                after={"email": user.email, "role": user.role},
                correlation_id=correlation_id,
                ip=ip,
            )
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError("Email already registered") from exc
        await self._session.refresh(user)
        return user

    async def login(
        self,
        *,
        email: str,
        password: str,
        correlation_id: str,
        ip: str | None,
        user_agent: str | None,
    ) -> AuthTokens:
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(User).where(User.email == email.strip().lower())
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise AuthenticationError("Invalid credentials")
        if user.status == UserStatus.DISABLED.value:
            raise AuthenticationError("Invalid credentials")
        if is_currently_locked(UserStatus(user.status), user.locked_until, now):
            raise AuthenticationError("Account temporarily locked")
        if not verify_password(password, user.password_hash):
            lock = register_failed_login(
                failed_attempts=user.failed_login_attempts,
                max_attempts=self._settings.login_max_attempts,
                now=now,
                lockout_seconds=self._settings.login_lockout_seconds,
                status=UserStatus(user.status),
            )
            user.failed_login_attempts = lock.failed_attempts
            user.status = lock.status.value
            user.locked_until = lock.locked_until
            await self._session.commit()
            if lock.status == UserStatus.LOCKED:
                raise AuthenticationError("Account temporarily locked")
            raise AuthenticationError("Invalid credentials")
        cleared = register_successful_login(now, user.locked_until)
        if cleared is None:
            raise AuthenticationError("Account temporarily locked")
        user.failed_login_attempts = 0
        user.status = UserStatus.ACTIVE.value
        user.locked_until = None
        tokens = await self._issue_tokens(user, ip=ip, user_agent=user_agent)
        self._session.add(
            ActivityLog(user_id=user.id, action="login", detail="success", ip=ip)
        )
        await self._queue_notification(user.id, "EMAIL", "auth.login", {"email": user.email})
        await self._audit(
            actor=user.id,
            action="user.login",
            entity_type="user",
            entity_id=user.id,
            after={"status": user.status},
            correlation_id=correlation_id,
            ip=ip,
        )
        await self._session.commit()
        return tokens

    async def logout(self, refresh_token: str, *, correlation_id: str, ip: str | None) -> None:
        token_hash = hash_token(refresh_token)
        result = await self._session.execute(
            select(Session).where(Session.refresh_token_hash == token_hash)
        )
        session = result.scalar_one_or_none()
        if session is None or session.revoked_at is not None:
            return
        session.revoked_at = datetime.now(UTC)
        self._session.add(
            ActivityLog(user_id=session.user_id, action="logout", ip=ip)
        )
        await self._audit(
            actor=session.user_id,
            action="user.logout",
            entity_type="session",
            entity_id=session.id,
            after={"revoked": True},
            correlation_id=correlation_id,
            ip=ip,
        )
        await self._session.commit()

    async def refresh(
        self, refresh_token: str, *, ip: str | None, user_agent: str | None
    ) -> AuthTokens:
        token_hash = hash_token(refresh_token)
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(Session).where(Session.refresh_token_hash == token_hash)
        )
        session = result.scalar_one_or_none()
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= now
        ):
            raise AuthenticationError("Invalid or expired token")
        session.revoked_at = now
        user = await self._session.get(User, session.user_id)
        if user is None or user.status == UserStatus.DISABLED.value:
            raise AuthenticationError("Invalid or expired token")
        tokens = await self._issue_tokens(user, ip=ip, user_agent=user_agent)
        await self._session.commit()
        return tokens

    async def request_recovery(self, email: str, *, correlation_id: str, ip: str | None) -> None:
        result = await self._session.execute(
            select(User).where(User.email == email.strip().lower())
        )
        user = result.scalar_one_or_none()
        if user is None:
            return
        raw = new_refresh_token()
        reset = PasswordReset(
            user_id=user.id,
            token_hash=hash_token(raw),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self._session.add(reset)
        payload: dict[str, object] = {"email": user.email, "template": "password_reset"}
        if self._settings.app_env in {"dev", "test", "ci"}:
            payload["token"] = raw
        await self._queue_notification(user.id, "EMAIL", "auth.password_reset", payload)
        await self._audit(
            actor=user.id,
            action="user.password_reset_requested",
            entity_type="user",
            entity_id=user.id,
            after={"reset_id": str(reset.id)},
            correlation_id=correlation_id,
            ip=ip,
        )
        await self._session.commit()

    async def confirm_recovery(self, token: str, new_password: str) -> None:
        validate_password(new_password)
        token_hash = hash_token(token)
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(PasswordReset).where(PasswordReset.token_hash == token_hash)
        )
        reset = result.scalar_one_or_none()
        if reset is None or reset.used_at is not None or reset.expires_at <= now:
            raise AuthenticationError("Invalid or expired token")
        user = await self._session.get(User, reset.user_id)
        if user is None:
            raise AuthenticationError("Invalid or expired token")
        user.password_hash = hash_password(new_password)
        reset.used_at = now
        await self._session.commit()

    async def get_user(self, user_id: UUID) -> User:
        user = await self._session.get(User, user_id)
        if user is None:
            raise AuthenticationError("Invalid or expired token")
        return user

    async def update_profile(
        self, user_id: UUID, *, full_name: str | None, phone: str | None
    ) -> User:
        user = await self.get_user(user_id)
        if full_name is not None:
            if not full_name.strip():
                raise ValidationError("Full name is required")
            user.full_name = full_name.strip()
        if phone is not None:
            user.phone = phone
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def list_activity(self, user_id: UUID) -> list[ActivityLog]:
        result = await self._session.execute(
            select(ActivityLog)
            .where(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(50)
        )
        return list(result.scalars())

    async def list_notifications(self, user_id: UUID) -> list[Notification]:
        result = await self._session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
        )
        return list(result.scalars())

    async def _issue_tokens(
        self, user: User, *, ip: str | None, user_agent: str | None
    ) -> AuthTokens:
        refresh = new_refresh_token()
        session = Session(
            id=uuid4(),
            user_id=user.id,
            refresh_token_hash=hash_token(refresh),
            expires_at=datetime.now(UTC) + timedelta(seconds=self._settings.refresh_ttl_seconds),
            ip=ip,
            user_agent=user_agent,
        )
        self._session.add(session)
        access = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
            secret=self._settings.jwt_secret.get_secret_value(),
            ttl_seconds=self._settings.jwt_access_ttl_seconds,
        )
        return AuthTokens(access_token=access, refresh_token=refresh, user=user)

    async def _queue_notification(
        self, user_id: UUID, channel: str, template: str, payload: dict[str, object]
    ) -> None:
        notification = Notification(
            user_id=user_id, channel=channel, template=template, payload=payload, status="QUEUED"
        )
        self._session.add(notification)
        self._session.add(
            OutboxEvent(
                event_type=f"notification.{template}",
                payload={"user_id": str(user_id), "channel": channel, "template": template},
            )
        )

    async def _audit(
        self,
        *,
        actor: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID,
        after: dict[str, object],
        correlation_id: str,
        ip: str | None,
        before: dict[str, object] | None = None,
    ) -> None:
        self._session.add(
            AuditEvent(
                actor_user_id=actor,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                before_state=before,
                after_state=after,
                correlation_id=correlation_id,
                ip=ip,
            )
        )
