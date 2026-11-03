from __future__ import annotations

import asyncio
from typing import TypedDict
from uuid import uuid4

import structlog
from sqlalchemy import select

from finbank.core.config import get_settings
from finbank.core.db import create_engine, create_session_factory
from finbank.core.logging import configure_logging
from finbank.core.security import hash_password
from finbank.domain.account_numbers import generate_account_number
from finbank.domain.enums import (
    AccountStatus,
    AccountType,
    Currency,
    LedgerDirection,
    OperationType,
    Role,
)
from finbank.models.banking import Account, LedgerEntry
from finbank.models.identity import User
from finbank.services.mapping import DEFAULT_DAILY, DEFAULT_PER_OPERATION

logger = structlog.get_logger(__name__)


class AccountSeed(TypedDict):
    number: str
    type: str
    currency: str
    balance: int
    status: str


class UserSeed(TypedDict):
    email: str
    password: str
    full_name: str
    role: str
    accounts: list[AccountSeed]


DEMO_USERS: list[UserSeed] = [
    {
        "email": "admin@finbank.test",
        "password": "AdminPassw0rd",
        "full_name": "Ada Admin",
        "role": Role.ADMIN.value,
        "accounts": [],
    },
    {
        "email": "support@finbank.test",
        "password": "SupportPassw0rd",
        "full_name": "Sam Support",
        "role": Role.SUPPORT.value,
        "accounts": [],
    },
    {
        "email": "ana@finbank.test",
        "password": "Customer1!",
        "full_name": "Ana Cliente",
        "role": Role.CUSTOMER.value,
        "accounts": [
            {
                "number": "32200000000000000001",
                "type": AccountType.CHECKING.value,
                "currency": Currency.ARS.value,
                "balance": 15_000_000,
                "status": AccountStatus.ACTIVE.value,
            },
            {
                "number": "32200000000000000002",
                "type": AccountType.SAVINGS.value,
                "currency": Currency.USD.value,
                "balance": 500_000,
                "status": AccountStatus.ACTIVE.value,
            },
        ],
    },
    {
        "email": "bruno@finbank.test",
        "password": "Customer1!",
        "full_name": "Bruno Cliente",
        "role": Role.CUSTOMER.value,
        "accounts": [
            {
                "number": "32200000000000000003",
                "type": AccountType.CHECKING.value,
                "currency": Currency.ARS.value,
                "balance": 2_000_000,
                "status": AccountStatus.ACTIVE.value,
            },
            {
                "number": "32200000000000000004",
                "type": AccountType.CHECKING.value,
                "currency": Currency.ARS.value,
                "balance": 100_000,
                "status": AccountStatus.BLOCKED.value,
            },
        ],
    },
    {
        "email": "cara@finbank.test",
        "password": "Customer1!",
        "full_name": "Cara SinSaldo",
        "role": Role.CUSTOMER.value,
        "accounts": [
            {
                "number": "32200000000000000005",
                "type": AccountType.CHECKING.value,
                "currency": Currency.ARS.value,
                "balance": 0,
                "status": AccountStatus.ACTIVE.value,
            }
        ],
    },
]


async def seed() -> None:
    settings = get_settings()
    configure_logging(settings)
    engine = create_engine(settings)
    factory = create_session_factory(engine)
    async with factory() as session:
        for spec in DEMO_USERS:
            existing = (
                await session.execute(select(User).where(User.email == spec["email"]))
            ).scalar_one_or_none()
            if existing is not None:
                continue
            user = User(
                id=uuid4(),
                email=spec["email"],
                password_hash=hash_password(spec["password"]),
                full_name=spec["full_name"],
                role=spec["role"],
                status="ACTIVE",
            )
            session.add(user)
            await session.flush()
            for account_spec in spec["accounts"]:
                balance = account_spec["balance"]
                account = Account(
                    id=uuid4(),
                    user_id=user.id,
                    account_number=account_spec["number"] or generate_account_number(),
                    type=str(account_spec["type"]),
                    currency=str(account_spec["currency"]),
                    status=str(account_spec["status"]),
                    available_balance=balance,
                    held_balance=0,
                    daily_transfer_limit=DEFAULT_DAILY,
                    per_operation_limit=DEFAULT_PER_OPERATION,
                )
                session.add(account)
                if balance > 0:
                    session.add(
                        LedgerEntry(
                            account_id=account.id,
                            operation_id=account.id,
                            operation_type=OperationType.ADJUSTMENT.value,
                            direction=LedgerDirection.CREDIT.value,
                            amount=balance,
                            currency=account.currency,
                            balance_after=balance,
                            description="Opening balance",
                        )
                    )
            logger.info("seeded_user", email=user.email)
        await session.commit()
    await engine.dispose()


def run() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    run()
