# Catálogo del Defect Injection Lab

Activación fail-closed (ADR-0007): solo si `APP_ENV` ∈ {`test`, `ci`}. En `dev`/`prod` los flags son no-op.

Formas de activar:

- `FINBANK_DEFECTS=DEF-FUN-001,DEF-DAT-001`
- Header `X-Finbank-Defects` (mismo formato), ignorado fuera de test/ci

Nunca activar en el stack de demo (`APP_ENV=dev`).

| ID | Categoría | Efecto | Detector OFF (debe pasar) |
| --- | --- | --- | --- |
| DEF-FUN-001 | Functional | `evaluate_transfer` omite NSF | `test_rejects_insufficient_funds` |
| DEF-AUT-001 | Authorization | `assert_can_operate_money` no-op | `test_only_customer_moves_money` |
| DEF-DAT-001 | Data | crédito de ledger en 0 | `test_completes_when_funds_and_limits_allow` |
| DEF-VAL-001 | Validation | `require_positive_amount` acepta ≤0 | `test_rejects_non_positive_amount` |
| DEF-SEC-001 | Security | `verify_password` siempre True | `test_verify_password_rejects_mismatch` |
| DEF-REL-001 | Reliability | no escribe outbox | `test_outbox_is_written_when_lab_off` |
| DEF-AUD-001 | Audit | no escribe `audit_events` | `test_audit_is_written_when_lab_off` |

Correr: `make qa-lab-detect`.
