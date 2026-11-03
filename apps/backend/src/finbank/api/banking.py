from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, Request

from finbank.api.deps import (
    client_ip,
    correlation_id,
    get_account_service,
    get_current_user,
    get_payment_service,
    get_transfer_service,
)
from finbank.api.schemas import (
    AccountOut,
    MovementOut,
    PaymentCreateRequest,
    PaymentOut,
    TransferCreateRequest,
    TransferOut,
)
from finbank.models.identity import User
from finbank.services.accounts import AccountService
from finbank.services.payments import PaymentService
from finbank.services.transfers import TransferService

router = APIRouter(prefix="/api/v1", tags=["banking"])


@router.get("/accounts")
async def list_accounts(
    user: Annotated[User, Depends(get_current_user)],
    accounts: Annotated[AccountService, Depends(get_account_service)],
) -> list[AccountOut]:
    items = await accounts.list_for_actor(user)
    return [AccountOut.model_validate(item) for item in items]


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    accounts: Annotated[AccountService, Depends(get_account_service)],
) -> AccountOut:
    item = await accounts.get(account_id, user)
    return AccountOut.model_validate(item)


@router.get("/accounts/{account_id}/movements")
async def list_movements(
    account_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    accounts: Annotated[AccountService, Depends(get_account_service)],
) -> list[MovementOut]:
    items = await accounts.movements(account_id, user)
    return [MovementOut.model_validate(item) for item in items]


@router.post("/transfers", status_code=201)
async def create_transfer(
    payload: TransferCreateRequest,
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    transfers: Annotated[TransferService, Depends(get_transfer_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> TransferOut:
    item = await transfers.create(
        actor=user,
        source_account_id=payload.source_account_id,
        destination_account_id=payload.destination_account_id,
        destination_account_number=payload.destination_account_number,
        amount=payload.amount,
        currency=payload.currency,
        idempotency_key=idempotency_key or str(uuid4()),
        correlation_id=correlation_id(request),
        ip=client_ip(request),
    )
    return TransferOut.model_validate(item)


@router.get("/transfers")
async def list_transfers(
    user: Annotated[User, Depends(get_current_user)],
    transfers: Annotated[TransferService, Depends(get_transfer_service)],
) -> list[TransferOut]:
    items = await transfers.list_for_actor(user)
    return [TransferOut.model_validate(item) for item in items]


@router.get("/transfers/{transfer_id}")
async def get_transfer(
    transfer_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    transfers: Annotated[TransferService, Depends(get_transfer_service)],
) -> TransferOut:
    item = await transfers.get(transfer_id, user)
    return TransferOut.model_validate(item)


@router.post("/payments", status_code=201)
async def create_payment(
    payload: PaymentCreateRequest,
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    payments: Annotated[PaymentService, Depends(get_payment_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> PaymentOut:
    item = await payments.create(
        actor=user,
        account_id=payload.account_id,
        amount=payload.amount,
        currency=payload.currency,
        payment_type=payload.payment_type,
        payee=payload.payee,
        idempotency_key=idempotency_key or str(uuid4()),
        scheduled_at=payload.scheduled_at,
        correlation_id=correlation_id(request),
        ip=client_ip(request),
    )
    return PaymentOut.model_validate(item)


@router.get("/payments")
async def list_payments(
    user: Annotated[User, Depends(get_current_user)],
    payments: Annotated[PaymentService, Depends(get_payment_service)],
) -> list[PaymentOut]:
    items = await payments.list_for_actor(user)
    return [PaymentOut.model_validate(item) for item in items]


@router.get("/payments/{payment_id}")
async def get_payment(
    payment_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    payments: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentOut:
    item = await payments.get(payment_id, user)
    return PaymentOut.model_validate(item)
