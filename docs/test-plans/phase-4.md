# Plan táctico — Fase 4 Functional testing

**DoD:** critical path verde en Chromium. Happy/negative/edge en API y E2E. Tags `@smoke` / `@regression` / `@critical`. Firefox/WebKit no obligatorios aquí (pipeline de main, Fase 10: `QA_BROWSERS=full`).

## Alcance

| Pieza | Dónde | Qué cubre |
| --- | --- | --- |
| API auth | `qa/automation/api/auth.functional.spec.ts` | 409, password débil, 401 genérico, lockout 423, logout/refresh, recovery un uso, perfil |
| API cuentas | `qa/automation/api/accounts.functional.spec.ts` | saldo entero, authz cruzada, 401, seed Ana |
| API transferencias | `qa/automation/api/transfers.functional.spec.ts` | entre clientes, insuficientes, idempotencia, moneda, límite por operación, BLOCKED, authz |
| API pagos | `qa/automation/api/payments.functional.spec.ts` | AYSA COMPLETED, REJECT sin débito, scheduled, idempotencia |
| API admin | `qa/automation/api/admin.functional.spec.ts` | listado, bloqueo, traza reducida, SUPPORT 403, CUSTOMER 403 |
| E2E Chromium | `qa/automation/e2e/**` | login negativo, logout, perfil, transfer, pago, admin block, SUPPORT solo lectura |

Datos: factories `qa+{uuid}@finbank.test`. Seed solo con tag `@seed`. Fondeo de clientes únicos desde Ana (no se afirma el saldo residual de Ana).

## Fuera de alcance (huecos justificados)

| Requisito | Por qué no en Fase 4 | Dónde vive |
| --- | --- | --- |
| FR-TRF-001 entre propias misma moneda | El registro crea una sola cuenta ARS; no hay alta de cuenta extra | Dominio Pytest; E2E cubre FR-TRF-002 |
| FR-TRF-004 límite diario acumulado | `per_operation` 5M < `daily` 20M; un solo POST no lo dispara | Dominio Pytest |
| FR-TRF-008 / FR-AUD-001 ledger+audit SQL | Sin GET de auditoría a propósito | Fase 6 — cumplido (`make qa-data`) |
| FR-PAY-003 ejecución del worker scheduled | El API deja SCHEDULED; el settle es worker | Fase 6 / integration |
| Firefox / WebKit | DoD: no obligatorios en el primer ciclo interno | `QA_BROWSERS=full` → Fase 10 |

## Cómo correr

```bash
make up
make qa-smoke        # @smoke (Fase 3)
make qa-regression   # @smoke|@regression|@critical en Docker
```

## Verificación (2026-11-03)

`make qa-regression` → **53 passed (15.4s)** en Docker, proyecto `e2e-chromium` + `api`.
