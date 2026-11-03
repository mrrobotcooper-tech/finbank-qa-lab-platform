from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
import structlog
import uvicorn
from fastapi import FastAPI, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from finbank.adapters.payment import HttpPaymentGateway
from finbank.adapters.rabbitmq import NOTIFICATIONS_QUEUE, RabbitChecker
from finbank.core.config import Settings, get_settings
from finbank.core.db import create_engine, create_session_factory
from finbank.core.logging import configure_logging
from finbank.models.banking import OutboxEvent
from finbank.services.payments import PaymentService

logger = structlog.get_logger(__name__)


def create_worker_app(
    settings: Settings,
    rabbit: RabbitChecker,
    *,
    enable_background: bool = True,
) -> FastAPI:
    engine: AsyncEngine | None = None
    session_factory = None
    gateway: HttpPaymentGateway | None = None
    if enable_background:
        engine = create_engine(settings)
        session_factory = create_session_factory(engine)
        gateway = HttpPaymentGateway(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.rabbit = rabbit
        app.state.settings = settings
        for attempt in range(1, 6):
            try:
                await rabbit.declare_topology()
                logger.info("worker_topology_ready", attempt=attempt)
                break
            except Exception:
                logger.warning("worker_topology_retry", attempt=attempt, exc_info=True)
                await asyncio.sleep(2)
        tasks: list[asyncio.Task[None]] = []
        if enable_background and session_factory is not None and gateway is not None:
            tasks = [
                asyncio.create_task(
                    _consume_notifications(rabbit, settings), name="notifications-consumer"
                ),
                asyncio.create_task(
                    _publish_outbox(session_factory, rabbit), name="outbox-publisher"
                ),
                asyncio.create_task(
                    _process_scheduled_payments(session_factory, gateway), name="scheduled-payments"
                ),
            ]
        app.state.worker_tasks = tasks
        yield
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await rabbit.close()
        if engine is not None:
            await engine.dispose()

    app = FastAPI(
        title="FinBank Worker",
        version="0.2.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )

    @app.get("/health")
    async def health(response: Response) -> dict[str, str]:
        if rabbit.is_connected():
            return {"status": "ok", "service": "finbank-worker"}
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "service": "finbank-worker"}

    return app


async def _publish_outbox(session_factory: object, rabbit: RabbitChecker) -> None:
    while True:
        try:
            async with session_factory() as session:  # type: ignore[operator]
                result = await session.execute(
                    select(OutboxEvent)
                    .where(OutboxEvent.published_at.is_(None))
                    .order_by(OutboxEvent.created_at.asc())
                    .limit(25)
                )
                events = list(result.scalars())
                for event in events:
                    await rabbit.publish(event.event_type, event.payload)
                    event.published_at = datetime.now(UTC)
                await session.commit()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("outbox_publish_retry", exc_info=True)
        await asyncio.sleep(2)


async def _process_scheduled_payments(session_factory: object, gateway: HttpPaymentGateway) -> None:
    while True:
        try:
            async with session_factory() as session:  # type: ignore[operator]
                processed = await PaymentService(session, gateway).process_due_scheduled()
                if processed:
                    logger.info("scheduled_payments_processed", count=processed)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("scheduled_payments_retry", exc_info=True)
        await asyncio.sleep(10)


async def _consume_notifications(rabbit: RabbitChecker, settings: Settings) -> None:
    client = httpx.AsyncClient(
        base_url=settings.notification_gateway_url,
        timeout=settings.dependency_timeout_seconds,
    )
    while True:
        try:
            await rabbit.declare_topology()
            connection = await rabbit.connect()
            channel = await connection.channel()
            queue = await channel.get_queue(NOTIFICATIONS_QUEUE)
            logger.info("worker_consuming", queue=NOTIFICATIONS_QUEUE)
            async with queue.iterator() as iterator:
                async for message in iterator:
                    async with message.process():
                        payload = _parse_payload(message.body)
                        await client.post("/notifications/email", json=payload)
                        logger.info(
                            "notification_delivered",
                            routing_key=message.routing_key,
                            user_id=payload.get("user_id"),
                        )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("worker_consumer_retry", exc_info=True)
            await asyncio.sleep(2)


def _parse_payload(body: bytes) -> dict[str, object]:
    try:
        data = json.loads(body.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def run() -> None:
    settings = get_settings()
    configure_logging(settings)
    rabbit = RabbitChecker(settings)
    app = create_worker_app(settings, rabbit)
    uvicorn.run(app, host="0.0.0.0", port=settings.worker_port, log_config=None)
