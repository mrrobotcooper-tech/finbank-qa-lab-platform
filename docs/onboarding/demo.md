# Demo de 15 minutos

FinBank es un banco **ficticio**. Nada de esto es dinero real.

## Antes (2 min)

```bash
cp .env.example .env   # si falta
make up
make ready
```

Web: http://localhost:5173 · API: http://localhost:8000/docs  
Ana: `ana@finbank.test` / `Customer1!` · destino Bruno CBU `32200000000000000003`.

## Guion

1. **Login Ana** → dashboard con saldos enteros (centavos, no float).
2. **Transferencia 1,00 ARS** a Bruno. Completada. Copiar el id.
3. **Auditoría sin API** (ADR-0005):

   ```bash
   make qa-data
   ```

   El test transfiere por HTTP, recibe 404 en `GET /api/v1/admin/audit` y afirma `ledger_entries` + `audit_events` por SQL con `finbank_qa_reader`.

4. **SUPPORT no mueve dinero:** `make qa-security` o login `support@finbank.test` / `SupportPassw0rd` e intentar transferir.

5. **Defect lab** (solo `APP_ENV=test`):

   ```bash
   make qa-lab-detect
   ```

   OFF: NSF rechaza. ON `DEF-FUN-001`: el mismo test falla. En `dev` el header `X-Finbank-Defects` no activa nada.

6. **CI fail-closed** (sin remoto):

   ```bash
   python3 scripts/ci/require-jobs.py --self-test
   NEEDS_JSON='{"qa-critical":{"result":"failure"}}' python3 scripts/ci/require-jobs.py; echo $?
   ```

   Debe imprimir NFR-CI-004 y salir 1.

## Si hay 5 minutos más

- Chaos: `make qa-chaos` (Redis 503, Rabbit no bloquea COMPLETED).
- Artillery: `make qa-perf` y abrir [docs/performance/](../performance/).
- Pact: `make qa-pact`.

## Cierre honesto

No afirmar WCAG AA, soak 24 h, ni un pipeline verde sin el run de Actions. Repo: [finbank-qa-lab-platform](https://github.com/mrrobotcooper-tech/finbank-qa-lab-platform). Recorte de números: [docs/evidence/2026-11-03.md](../evidence/2026-11-03.md).
