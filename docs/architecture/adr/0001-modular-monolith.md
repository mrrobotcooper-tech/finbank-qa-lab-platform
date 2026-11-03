# ADR-0001 — Monolito modular

**Estado:** Propuesto  
**Fase:** 0

## Contexto

El SUT debe parecer un sistema financiero real (API, worker, colas, caché, mocks) sin convertir el laboratorio en un ejercicio de Kubernetes.

## Alternativas

| Opción | Ventaja | Costo |
| --- | --- | --- |
| Microservicios por dominio | Parece “enterprise” | Sagas, contratos explosivos, data testing fragmentado |
| Monolito clásico sin worker | Simple | No hay asincronía real que probar |
| **Monolito modular + worker + mocks** | Atómica el dinero; chaos y async reales | Diagrama menos “enterprise” |

## Decisión

Un paquete Python `finbank` con límites de módulo (auth, accounts, transfers, payments, admin, audit). Dos procesos: API y worker. Frontend separado. Mocks en contenedor propio.

## Consecuencias

- Transferencias con ledger en una transacción SQL.
- QA consulta una base para reconciliación.
- Chaos testing sigue siendo significativo (Redis, Postgres, Rabbit, mock down).
- No se documentará como arquitectura de microservicios.
