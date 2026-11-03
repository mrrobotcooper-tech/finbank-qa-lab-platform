# Plan táctico — Fase 6 Data testing

**DoD:** un test transfiere por API y afirma `audit_events` y ledger **sin** GET de auditoría.

## Alcance

| Spec | Requisito |
| --- | --- |
| `data/transfer.ledger-audit.spec.ts` | FR-TRF-008/010, FR-AUD-001, 404 de GET /audit |
| `data/reconciliation.spec.ts` | FR-ACCT-006, idempotencia SQL, rechazo sin ledger |
| `data/payment.ledger.spec.ts` | FR-PAY-001/004 |
| `data/audit.append-only.spec.ts` | FR-AUD-002 |

Rol DB: `finbank_qa_reader` (SELECT). Queries de evidencia: `database/scripts/evidence_transfer.sql`.

## Cómo correr

```bash
make qa-data
make qa-bdd    # el escenario COMPLETED también lee SQL
```

## Verificación

- `make qa-data`: **7 tests** Playwright proyecto `data`.
- DoD: transferencia API + 404 de GET `/api/v1/admin/audit` + SELECT `ledger_entries` (2 asientos) + SELECT `audit_events`.
- El rol `finbank_qa_reader` recibe `permission denied` en UPDATE/INSERT.
