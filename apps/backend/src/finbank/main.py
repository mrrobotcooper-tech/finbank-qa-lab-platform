from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finbank.adapters.payment import HttpPaymentGateway
from finbank.adapters.postgres import PostgresChecker
from finbank.adapters.rabbitmq import RabbitChecker
from finbank.adapters.redis_client import RedisChecker
from finbank.api.admin import router as admin_router
from finbank.api.auth import me_router
from finbank.api.auth import router as auth_router
from finbank.api.banking import router as banking_router
from finbank.api.errors import register_exception_handlers
from finbank.api.health import router as health_router
from finbank.core.config import Settings, get_settings
from finbank.core.correlation import CorrelationIdMiddleware
from finbank.core.db import create_session_factory
from finbank.core.defect_middleware import DefectHeaderMiddleware
from finbank.core.defects import configure_startup_defects
from finbank.core.http_metrics import HttpMetricsMiddleware
from finbank.core.logging import configure_logging
from finbank.core.security_headers import SecurityHeadersMiddleware
from finbank.services.health import HealthService

logger = structlog.get_logger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    health_service: HealthService | None = None,
) -> FastAPI:
    resolved = settings or get_settings()
    configure_logging(resolved)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = resolved
        app.state.active_defects = configure_startup_defects(
            resolved.app_env, resolved.finbank_defects
        )
        if health_service is not None:
            app.state.health_service = health_service
            app.state.postgres = None
            app.state.redis = None
            app.state.rabbit = None
            app.state.session_factory = None
            app.state.payment_gateway = None
        else:
            postgres = PostgresChecker(resolved)
            redis = RedisChecker(resolved)
            rabbit = RabbitChecker(resolved)
            app.state.postgres = postgres
            app.state.redis = redis
            app.state.rabbit = rabbit
            app.state.health_service = HealthService((postgres, redis, rabbit))
            app.state.session_factory = create_session_factory(postgres.engine)
            app.state.payment_gateway = HttpPaymentGateway(resolved)
            try:
                await rabbit.declare_topology()
            except Exception:
                logger.warning("rabbitmq_topology_deferred", exc_info=True)
        logger.info(
            "api_starting",
            env=resolved.app_env,
            defects=sorted(app.state.active_defects),
        )
        yield
        if postgres := app.state.postgres:
            await postgres.dispose()
        if redis := app.state.redis:
            await redis.close()
        if rabbit := app.state.rabbit:
            await rabbit.close()
        logger.info("api_stopped")

    application = FastAPI(
        title="FinBank API",
        version="0.2.0",
        description="Fictional digital banking System Under Test for a QA laboratory.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.state.settings = resolved
    application.add_middleware(HttpMetricsMiddleware)
    application.add_middleware(CorrelationIdMiddleware, settings=resolved)
    application.add_middleware(DefectHeaderMiddleware, settings=resolved)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved.public_web_url],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            resolved.correlation_header,
            "Content-Type",
            "Idempotency-Key",
            "X-Finbank-Defects",
        ],
    )
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(auth_router)
    application.include_router(me_router)
    application.include_router(banking_router)
    application.include_router(admin_router)
    return application


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "finbank.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "dev",
    )
