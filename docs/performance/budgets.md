# Presupuestos NFR-PERF recalibrados

Fuente: [measurement-2026-11-03.md](measurement-2026-11-03.md). No son SLAs de industria.

| ID | Presupuesto inicial (Fase 0) | Medido | Presupuesto vigente |
| --- | --- | --- | --- |
| NFR-PERF-001 | Login p95 < 500 ms a 20 RPS | p95 **459.5 ms** a **10 RPS** (220 req, 0 errores) | Login p95 < **600 ms** a **10 RPS** sostenidos. 20 RPS no se sostiene en este lab (Argon2). |
| NFR-PERF-002 | Cuentas p95 < 400 ms a 50 RPS | p95 **13.1 ms** a **20 RPS** (440 req) | Cuentas p95 < **100 ms** a **20 RPS**. 50 RPS no medido; no se afirma. |
| NFR-PERF-003 | Transfer p95 < 800 ms a 10 RPS | p95 **22.9 ms** a **3 RPS** (68 POST 1 ¢, 201) | Transfer p95 < **100 ms** a **3 RPS** sobre una sola cuenta origen. 10 RPS concurrentes no se afirma (FOR UPDATE). |
| NFR-PERF-004 | Error rate < 1 % | **0 %** en login, cuentas y transfers | Error rate < **1 %** en el load nominal de la tabla anterior. |
| NFR-PERF-005 | Soak/stress no bloquean PRs | No corrido | Sin cambio: nightly/manual, no gate de PR. |

Los YAML en `qa/automation/performance/` están alineados a las tasas vigentes (10 / 20 / 3 RPS).
