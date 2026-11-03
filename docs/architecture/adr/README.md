# Architecture Decision Records

Los ADR registran decisiones que no deben revertirse sin discusión. Formato: contexto, alternativas, decisión, consecuencias.

| ID | Título | Estado |
| --- | --- | --- |
| [0001](0001-modular-monolith.md) | Monolito modular en lugar de microservicios | Aceptado |
| [0002](0002-ledger-as-source-of-truth.md) | Ledger como fuente de verdad del dinero | Aceptado |
| [0003](0003-auth-jwt-redis.md) | JWT de acceso + refresh opaco en Redis | Aceptado |
| [0004](0004-money-as-integer-cents.md) | Dinero en enteros de unidad menor | Aceptado |
| [0005](0005-audit-without-public-api.md) | Auditoría append-only sin listado público | Aceptado |
| [0006](0006-independent-qa-framework.md) | Framework QA independiente del SUT | Aceptado |
| [0007](0007-defect-injection-isolation.md) | Defect lab aislado por entorno | Aceptado |
| [0008](0008-dual-ci.md) | GitHub Actions primario + GitLab CI portable | Aceptado |
| [0009](0009-bdd-dual-runner.md) | Playwright Test + Cucumber, una librería | Aceptado |
| [0010](0010-outbox-and-mocks.md) | Outbox transaccional y pasarela mock propia | Aceptado |
| [0011](0011-observability.md) | Observabilidad pragmática (logs, métricas, correlation ID) | Aceptado |
| [0012](0012-host-port-mapping.md) | Puertos internos vs publicados en el host | Aceptado |

Fase 0 aprobada el 2026-11-03. Los ADR de dominio (ledger, auth, mocks) se implementan a partir de la Fase 2; los de runtime (monolito, observabilidad, defect fail-closed) ya están materializados en la foundation.
