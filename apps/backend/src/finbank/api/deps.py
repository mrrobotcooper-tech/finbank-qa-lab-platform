from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from finbank.adapters.payment import PaymentGateway
from finbank.core.config import Settings
from finbank.core.security import decode_access_token
from finbank.domain.errors import AuthenticationError
from finbank.models.identity import User
from finbank.services.accounts import AccountService
from finbank.services.admin import AdminService
from finbank.services.auth import AuthService
from finbank.services.health import HealthService
from finbank.services.payments import PaymentService
from finbank.services.transfers import TransferService

bearer = HTTPBearer(auto_error=False)


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[no-any-return]


def get_health_service(request: Request) -> HealthService:
    return request.app.state.health_service  # type: ignore[no-any-return]


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    factory = getattr(request.app.state, "session_factory", None)
    if factory is None:
        raise AuthenticationError("Application is not ready")
    return factory  # type: ignore[no-any-return]


async def get_session(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        yield session


def get_payment_gateway(request: Request) -> PaymentGateway:
    return request.app.state.payment_gateway  # type: ignore[no-any-return]


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> AuthService:
    return AuthService(session, settings)


def get_account_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AccountService:
    return AccountService(session)


def get_transfer_service(session: Annotated[AsyncSession, Depends(get_session)]) -> TransferService:
    return TransferService(session)


def get_payment_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    gateway: Annotated[PaymentGateway, Depends(get_payment_gateway)],
) -> PaymentService:
    return PaymentService(session, gateway)


def get_admin_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AdminService:
    return AdminService(session)


async def get_current_user(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings_dep)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Not authenticated")
    payload = decode_access_token(credentials.credentials, settings.jwt_secret.get_secret_value())
    return await auth.get_user(UUID(str(payload["sub"])))


def correlation_id(request: Request) -> str:
    return str(getattr(request.state, "correlation_id", ""))


def client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None
