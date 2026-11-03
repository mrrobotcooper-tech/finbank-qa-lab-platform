from __future__ import annotations

import asyncio
import json
from typing import Any

import aio_pika
from aio_pika.abc import AbstractRobustConnection

from finbank.adapters.health import ComponentStatus
from finbank.core.config import Settings

EVENTS_EXCHANGE = "finbank.events"
NOTIFICATIONS_QUEUE = "finbank.notifications"
NOTIFICATIONS_BINDING = "notification.#"


class RabbitChecker:
    name = "rabbitmq"

    def __init__(
        self,
        settings: Settings,
        connection: AbstractRobustConnection | None = None,
    ) -> None:
        self._settings = settings
        self._connection = connection
        self._owned = connection is None

    @property
    def connection(self) -> AbstractRobustConnection | None:
        return self._connection

    async def connect(self) -> AbstractRobustConnection:
        if self._connection is not None and not self._connection.is_closed:
            return self._connection
        self._connection = await aio_pika.connect_robust(
            self._settings.rabbitmq_url,
            timeout=self._settings.dependency_timeout_seconds,
        )
        return self._connection

    async def declare_topology(self) -> None:
        connection = await self.connect()
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            EVENTS_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=NOTIFICATIONS_BINDING)
        await channel.close()

    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        connection = await self.connect()
        channel = await connection.channel()
        exchange = await channel.get_exchange(EVENTS_EXCHANGE)
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
        await channel.close()

    async def check(self) -> ComponentStatus:
        try:
            connection = await asyncio.wait_for(
                self.connect(),
                timeout=self._settings.dependency_timeout_seconds,
            )
            if connection.is_closed:
                return ComponentStatus(name=self.name, status="down", detail="connection closed")
            return ComponentStatus(name=self.name, status="up")
        except Exception as exc:  # noqa: BLE001
            return ComponentStatus(
                name=self.name,
                status="down",
                detail=None if self._settings.app_env == "prod" else str(exc)[:240],
            )

    def is_connected(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    async def close(self) -> None:
        if self._owned and self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
