from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from finbank.api.deps import client_ip, correlation_id, get_admin_service, get_current_user
from finbank.api.schemas import (
    AccountOut,
    AdminAccountUpdateRequest,
    AdminUserUpdateRequest,
    PaymentOut,
    TransferOut,
    UserOut,
)
from finbank.models.identity import User
from finbank.services.admin import AdminService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    actor: Annotated[User, Depends(get_current_user)],
    admin: Annotated[AdminService, Depends(get_admin_service)],
) -> list[UserOut]:
    items = await admin.list_users(actor)
    return [UserOut.model_validate(item) for item in items]


@router.patch("/users/{user_id}")
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    request: Request,
    actor: Annotated[User, Depends(get_current_user)],
    admin: Annotated[AdminService, Depends(get_admin_service)],
) -> UserOut:
    item = await admin.update_user(
        actor,
        user_id,
        status=payload.status,
        role=payload.role,
        correlation_id=correlation_id(request),
        ip=client_ip(request),
    )
    return UserOut.model_validate(item)


@router.patch("/accounts/{account_id}")
async def update_account(
    account_id: UUID,
    payload: AdminAccountUpdateRequest,
    request: Request,
    actor: Annotated[User, Depends(get_current_user)],
    admin: Annotated[AdminService, Depends(get_admin_service)],
) -> AccountOut:
    item = await admin.update_account_status(
        actor,
        account_id,
        payload.status,
        correlation_id=correlation_id(request),
        ip=client_ip(request),
    )
    return AccountOut.model_validate(item)


@router.get("/operations")
async def operations(
    actor: Annotated[User, Depends(get_current_user)],
    admin: Annotated[AdminService, Depends(get_admin_service)],
) -> dict[str, list[TransferOut] | list[PaymentOut]]:
    data = await admin.operations(actor)
    return {
        "transfers": [TransferOut.model_validate(item) for item in data["transfers"]],
        "payments": [PaymentOut.model_validate(item) for item in data["payments"]],
    }


@router.get("/indicators")
async def indicators(
    actor: Annotated[User, Depends(get_current_user)],
    admin: Annotated[AdminService, Depends(get_admin_service)],
) -> dict[str, int]:
    return await admin.indicators(actor)


@router.get("/operations/{transfer_id}")
async def operation_trace(
    transfer_id: UUID,
    actor: Annotated[User, Depends(get_current_user)],
    admin: Annotated[AdminService, Depends(get_admin_service)],
) -> dict[str, object]:
    return await admin.operation_trace(actor, transfer_id)


@router.get("/audit")
async def audit_forbidden() -> dict[str, str]:
    """Intentionally absent: full audit is SQL-only (FR-AUD-003)."""
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Complete audit history is not exposed via API")
