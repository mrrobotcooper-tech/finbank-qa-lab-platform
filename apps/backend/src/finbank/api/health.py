from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from finbank.core.config import Settings
from finbank.core.metrics import render_metrics
from finbank.services.health import HealthService

router = APIRouter(tags=["health"])


def get_settings_from_app(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[no-any-return]


def get_health_from_app(request: Request) -> HealthService:
    return request.app.state.health_service  # type: ignore[no-any-return]


@router.get("/health")
async def liveness(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings_from_app)],
) -> dict[str, str]:
    correlation_id = getattr(request.state, "correlation_id", "")
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "correlation_id": correlation_id,
    }


@router.get("/ready")
async def readiness(
    request: Request,
    response: Response,
    health: Annotated[HealthService, Depends(get_health_from_app)],
) -> dict[str, object]:
    overall, components = await health.readiness()
    if overall != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    correlation_id = getattr(request.state, "correlation_id", "")
    return {
        "status": overall,
        "correlation_id": correlation_id,
        "components": [item.to_dict() for item in components],
    }


@router.get("/metrics")
async def metrics() -> Response:
    payload = render_metrics()
    return Response(content=payload, media_type="text/plain; version=0.0.4; charset=utf-8")
