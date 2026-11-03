# Plan táctico — Fase 8 Performance

**DoD:** umbrales basados en medición, no en fantasía. Informe en `docs/performance/`.

## Alcance

| Pieza | Dónde |
| --- | --- |
| Login | `qa/automation/performance/login.yml` |
| Cuentas | `qa/automation/performance/accounts.yml` |
| Transferencias 1¢ | `qa/automation/performance/transfers.yml` |
| Runner host | `make qa-perf` → `qa/reports/perf/` |
| Presupuestos | `docs/performance/budgets.md` |

Artillery corre **en el host** contra `http://127.0.0.1:8000` (ADR-0012). No dentro del contenedor `qa`.

## Cómo correr

```bash
make up
make qa-perf
```

## Recalibración

Los NFR-PERF-001–004 iniciales eran hipótesis. Tras la corrida se documentan p50/p95 reales y se ajustan los presupuestos a lo que este Docker local sostiene. Soak/stress (NFR-PERF-005) no bloquean PRs.

## Verificación (2026-11-03)

| Escenario | RPS | p50 | p95 | Requests | Errores |
| --- | ---: | ---: | ---: | ---: | ---: |
| login | 10 | 262.5 ms | 459.5 ms | 220 | 0 |
| accounts | 20 | 4 ms | 13.1 ms | 440 | 0 |
| transfers 1 ¢ | 3 | 12.1 ms | 22.9 ms | 68 | 0 |

Presupuestos vigentes: [docs/performance/budgets.md](../performance/budgets.md).
