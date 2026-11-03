from __future__ import annotations


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"


class AuthenticationError(DomainError):
    code = "AUTHENTICATION_ERROR"


class AuthorizationError(DomainError):
    code = "AUTHORIZATION_ERROR"


class ConflictError(DomainError):
    code = "CONFLICT"
