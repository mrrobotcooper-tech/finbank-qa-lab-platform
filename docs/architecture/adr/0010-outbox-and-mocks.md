# ADR-0010 — Outbox transaccional y pasarela mock propia

**Estado:** Propuesto

## Contexto

Publicar a RabbitMQ dentro de la transacción SQL no es transaccional. Llamar a un adquirente real está prohibido. WireMock es útil, pero un mock propio permite defectos de latencia y contrato versionado junto al SUT.

## Decisión

1. Eventos de negocio (notificaciones) salen por **outbox**: se insertan en PostgreSQL en el mismo commit que el ledger; un publisher los envía a RabbitMQ.
2. `finbank-mocks` es un servicio HTTP mínimo (pagos y envío de email/SMS) configurable por escenario (OK, reject, 5s delay, 500).
3. En unidad, puertos inyectados (`PaymentGateway`, `NotificationGateway`).
4. En QA de red, se pueden usar definiciones equivalentes en `qa/mocks` (WireMock o el propio servicio).

## Consecuencias

- Chaos de Rabbit no corrompe saldos; deja outbox pendiente — data test de primer nivel.
- Contract testing puede apuntar a `finbank-mocks` y a `finbank-api`.
- No se fingirá “email enviado” solo porque el API devolvió 201.
