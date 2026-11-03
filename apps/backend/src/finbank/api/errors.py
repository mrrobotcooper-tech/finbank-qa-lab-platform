from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from finbank.domain.errors import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthenticationError)
    async def auth_handler(_request: Request, exc: AuthenticationError) -> JSONResponse:
        status = 423 if "locked" in str(exc).lower() else 401
        return JSONResponse({"detail": str(exc), "code": exc.code}, status_code=status)

    @app.exception_handler(AuthorizationError)
    async def authz_handler(_request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse({"detail": str(exc), "code": exc.code}, status_code=403)

    @app.exception_handler(ConflictError)
    async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse({"detail": str(exc), "code": exc.code}, status_code=409)

    @app.exception_handler(ValidationError)
    async def validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse({"detail": str(exc), "code": exc.code}, status_code=422)

    @app.exception_handler(DomainError)
    async def domain_handler(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse({"detail": str(exc), "code": exc.code}, status_code=400)
