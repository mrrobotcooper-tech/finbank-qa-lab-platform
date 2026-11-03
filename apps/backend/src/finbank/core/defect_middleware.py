from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from finbank.core.config import Settings
from finbank.core.defects import DEFECT_HEADER, bind_request_defects, reset_request_defects


class DefectHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        super().__init__(app)
        self._settings = settings

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        token = bind_request_defects(self._settings.app_env, request.headers.get(DEFECT_HEADER, ""))
        try:
            return await call_next(request)
        finally:
            reset_request_defects(token)
