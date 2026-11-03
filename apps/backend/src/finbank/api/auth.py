from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from finbank.api.deps import (
    client_ip,
    correlation_id,
    get_auth_service,
    get_current_user,
    get_settings_dep,
)
from finbank.api.schemas import (
    ActivityOut,
    LoginRequest,
    NotificationOut,
    ProfileUpdateRequest,
    RecoveryConfirmRequest,
    RecoveryRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from finbank.core.config import Settings
from finbank.models.identity import User
from finbank.services.auth import AuthService, AuthTokens

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
me_router = APIRouter(prefix="/api/v1", tags=["me"])
REFRESH_COOKIE = "finbank_refresh"


def _set_refresh_cookie(response: Response, tokens: AuthTokens, settings: Settings) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=tokens.refresh_token,
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "prod",
        max_age=settings.refresh_ttl_seconds,
        path="/api/v1/auth",
    )


def _token_payload(tokens: AuthTokens) -> TokenResponse:
    return TokenResponse(access_token=tokens.access_token, user=UserOut.model_validate(tokens.user))


@router.post("/register", status_code=201)
async def register(
    payload: RegisterRequest,
    request: Request,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserOut:
    user = await auth.register(
        email=str(payload.email),
        password=payload.password,
        full_name=payload.full_name,
        phone=payload.phone,
        correlation_id=correlation_id(request),
        ip=client_ip(request),
    )
    return UserOut.model_validate(user)


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> TokenResponse:
    tokens = await auth.login(
        email=str(payload.email),
        password=payload.password,
        correlation_id=correlation_id(request),
        ip=client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    _set_refresh_cookie(response, tokens, settings)
    return _token_payload(tokens)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    token = request.cookies.get(REFRESH_COOKIE, "")
    if token:
        await auth.logout(token, correlation_id=correlation_id(request), ip=client_ip(request))
    response.delete_cookie(REFRESH_COOKIE, path="/api/v1/auth")
    return {"status": "ok"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    auth: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> TokenResponse:
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        from finbank.domain.errors import AuthenticationError

        raise AuthenticationError("Invalid or expired token")
    tokens = await auth.refresh(
        token, ip=client_ip(request), user_agent=request.headers.get("user-agent")
    )
    _set_refresh_cookie(response, tokens, settings)
    return _token_payload(tokens)


@router.post("/recovery")
async def recovery(
    payload: RecoveryRequest,
    request: Request,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    await auth.request_recovery(
        str(payload.email), correlation_id=correlation_id(request), ip=client_ip(request)
    )
    return {"status": "ok"}


@router.post("/recovery/confirm")
async def recovery_confirm(
    payload: RecoveryConfirmRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    await auth.confirm_recovery(payload.token, payload.password)
    return {"status": "ok"}


@me_router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return UserOut.model_validate(user)


@me_router.patch("/me")
async def update_me(
    payload: ProfileUpdateRequest,
    user: Annotated[User, Depends(get_current_user)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserOut:
    updated = await auth.update_profile(user.id, full_name=payload.full_name, phone=payload.phone)
    return UserOut.model_validate(updated)


@me_router.get("/me/activity")
async def activity(
    user: Annotated[User, Depends(get_current_user)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> list[ActivityOut]:
    items = await auth.list_activity(user.id)
    return [ActivityOut.model_validate(item) for item in items]


@me_router.get("/me/notifications")
async def notifications(
    user: Annotated[User, Depends(get_current_user)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> list[NotificationOut]:
    items = await auth.list_notifications(user.id)
    return [NotificationOut.model_validate(item) for item in items]
