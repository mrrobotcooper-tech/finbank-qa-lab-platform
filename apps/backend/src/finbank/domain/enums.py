from enum import StrEnum


class Role(StrEnum):
    CUSTOMER = "CUSTOMER"
    SUPPORT = "SUPPORT"
    ADMIN = "ADMIN"


class UserStatus(StrEnum):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    DISABLED = "DISABLED"


class AccountType(StrEnum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class AccountStatus(StrEnum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"


class Currency(StrEnum):
    ARS = "ARS"
    USD = "USD"


class TransferStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class PaymentType(StrEnum):
    SERVICE = "SERVICE"
    CARD = "CARD"
    INVOICE = "INVOICE"
    SCHEDULED = "SCHEDULED"


class LedgerDirection(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class OperationType(StrEnum):
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    FEE = "FEE"
    ADJUSTMENT = "ADJUSTMENT"
