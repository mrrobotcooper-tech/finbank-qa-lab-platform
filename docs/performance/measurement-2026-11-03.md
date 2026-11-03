# Medición Artillery — 2026-11-03

**Entorno:** Docker Compose local, API `http://127.0.0.1:8000`, host Linux.  
**Herramienta:** Artillery 2 vía `make qa-perf`.  
**Actor:** `ana@finbank.test` (seed). Destino de transfer: CBU Bruno `32200000000000000003`.  
**Artefacto:** `qa/reports/perf/summary.json` (gitignored).

Hora de cierre del resumen: `2026-11-03T23:01:08.595Z`.

| Escenario | RPS sostenido | Duración sustain | Requests | 2xx | Error rate | min | p50 | p95 | p99 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| POST `/api/v1/auth/login` | 10 | 20 s (+10 s warmup @2) | 220 | 220 | 0 % | 82 ms | 262.5 ms | 459.5 ms | 550.1 ms | 592 ms |
| GET `/api/v1/accounts` | 20 | 20 s (+8 s warmup @5) | 440 | 440 | 0 % | 3 ms | 4 ms | 13.1 ms | 295.9 ms | 581 ms |
| POST `/api/v1/transfers` (1 ¢) | 3 | 20 s (+8 s warmup @1) | 68 | 68 (201) | 0 % | 10 ms | 12.1 ms | 22.9 ms | 25.8 ms | 35 ms |

## Notas honestas

- Login usa Argon2: el p95 ~460 ms a 10 RPS ya empuja CPU. No se sostuvo 20 RPS (presupuesto inicial). Un intervalo intermedio del sustain marcó p95 528 ms; el agregado quedó en 459.5 ms.
- Cuentas es lectura autenticada con token cacheado en el processor. p95 13 ms; p99/max altos por cola en frío. No se corrió 50 RPS.
- Transferencias van a la **misma** checking ARS de Ana (`SELECT FOR UPDATE`). 3 RPS serializa bien; 10 RPS concurrentes sobre la misma fila no se afirma.
- Error rate 0 % en los tres escenarios. NFR-PERF-004 se mantiene en < 1 %.
- Soak/stress  (NFR-PERF-005) no forman parte de esta corrida ni de PRs.
