# Plan táctico — Fase 3 QA framework core

**DoD:** `make qa-smoke` en Docker. Cero tests vacíos. POM de login y cuentas. Fixtures de rol y cliente HTTP.

## Alcance

| Pieza | Dónde | Qué cubre |
| --- | --- | --- |
| Config + HTTP + Zod | `qa/automation/framework` | URLs, correlation ID, contratos de smoke |
| Fixtures | `fixtures.ts` | `api`, `customerDraft`, `seedCustomer`, `seedAdmin`, POM |
| POM | `pages/` | Login, registro, dashboard de cuentas |
| API smoke | `automation/api` | `/health`, `/ready`, registro, 401, audit 404 |
| E2E smoke | `automation/e2e` | Login Ana (`@seed`) y registro UI de cliente único |

## Fuera de alcance (fases siguientes)

Cucumber, matrix funcional, data SQL, axe, Artillery, Pact, defect lab.

## Cómo correr

```bash
make up          # SUT
make qa-smoke    # imagen Playwright + Chromium contra web/api
```

## Verificación (2026-11-03)

`docker compose --profile qa run --rm --build qa` → **8 passed (3.9s)**.

| Spec | Cobertura |
| --- | --- |
| `api/health.smoke.spec.ts` | `/health`, `/ready` (postgres/redis/rabbitmq), `GET /api/v1/admin/audit` 404 |
| `api/auth.smoke.spec.ts` | registro+login+cuentas de cliente único; 401; seed Ana `@seed` |
| `e2e/auth/login.smoke.spec.ts` | login Ana → dashboard; registro UI + login → 1 cuenta |
