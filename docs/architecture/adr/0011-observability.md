# ADR-0011 — Observabilidad pragmática

**Estado:** Propuesto

## Contexto

El SUT debe ser investigable (correlation ID, logs, métricas) sin convertir Fase 1 en un proyecto de tracing distribuido.

## Decisión

Fase 1–2: `structlog` JSON, header `X-Correlation-ID`, Prometheus `/metrics`, Grafana provisionado, healthchecks.

OpenTelemetry traces: opcional a partir de Fase 8 si el relato de performance/chaos lo necesita. No es bloqueante.

## Consecuencias

- Chaos y data tests pueden correlacionar por ID desde el día uno.
- No se afirmará “tracing distribuido” hasta que exista.
