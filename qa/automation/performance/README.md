# Performance (Artillery)

Escenarios contra la API publicada en el host (`http://127.0.0.1:8000`), no desde el contenedor `qa`.

| Archivo | Flujo | Usuario |
| --- | --- | --- |
| `login.yml` | POST `/api/v1/auth/login` | Ana |
| `accounts.yml` | GET `/api/v1/accounts` | Ana (token cacheado) |
| `transfers.yml` | POST 1 centavo a Bruno | Ana, `Idempotency-Key` única |

```bash
make qa-perf
```

Informe y presupuestos recalibrados: `docs/performance/`. Artefactos JSON: `qa/reports/perf/` (gitignored).
