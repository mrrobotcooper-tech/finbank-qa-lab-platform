# ADR-0005 — Auditoría sin listado público

**Estado:** Propuesto

## Contexto

El módulo de Data Testing debe demostrar que QA verifica requisitos aunque no exista un endpoint. Inventar `GET /audit` para “hacer fácil el test” invalida ese ejercicio del laboratorio.

## Decisión

`audit_events` es append-only. No hay API de listado completo. Puede existir una vista operativa reducida para ADMIN (FR-AUD-004) que **no** incluye before/after completos.

La evidencia de FR-AUD-001 y FR-TRF-010 es SQL.

## Consecuencias

- El framework QA necesita acceso de lectura a PostgreSQL.
- Hay que cuidar que ese acceso no se use como atajo para aserciones que sí pertenecen a la API (saldos visibles, estados de transferencia).
- Documentar el rol DB `finbank_qa_reader` en Fase 1.
