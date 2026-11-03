from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from finbank.core.metrics import HTTP_LATENCY, HTTP_REQUESTS

_SKIP = {"/metrics"}


class HttpMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        if path in _SKIP:
            return await call_next(request)
        started = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - started
        HTTP_REQUESTS.labels(
            method=request.method, path=path, status=str(response.status_code)
        ).inc()
        HTTP_LATENCY.labels(method=request.method, path=path).observe(elapsed)
        return response
