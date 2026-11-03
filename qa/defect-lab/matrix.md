# Matriz de detección

Cada fila es un defecto del catálogo. OFF = suite verde. ON = el detector nombrado **falla**.

| Defecto | OFF | ON (esperado) | Evidencia |
| --- | --- | --- | --- |
| DEF-FUN-001 | `test_rejects_insufficient_funds` PASS | el mismo test FAIL | `make qa-lab-detect` |
| DEF-AUT-001 | `test_only_customer_moves_money` PASS | FAIL | idem |
| DEF-DAT-001 | `test_completes_when_funds_and_limits_allow` PASS | FAIL (crédito ≠ débito) | idem |
| DEF-VAL-001 | `test_rejects_non_positive_amount` PASS | FAIL | idem |
| DEF-SEC-001 | `test_verify_password_rejects_mismatch` PASS | FAIL | idem |
| DEF-REL-001 | `test_outbox_is_written_when_lab_off` PASS | FAIL | idem |
| DEF-AUD-001 | `test_audit_is_written_when_lab_off` PASS | FAIL | idem |

DoD Fase 9: al menos un defecto ON rompe un test concreto. El script exige los siete.
