# RTM viva — IDs reales

**Documento:** RTM-002  
**Fase:** 11  
**Regla:** cada FR crítico tiene al menos un test ejecutable o un hueco justificado. Sin IDs inventados.

Leyenda: U unit · I integration · A API · E E2E · B BDD · D data/SQL

## Autenticación

| Req | Pri | Tests reales |
| --- | --- | --- |
| FR-AUTH-001 | C | U `test_password.py` · A `api/auth.functional.spec.ts` · E `e2e/auth/login.smoke.spec.ts` · B `bdd/features/auth.feature` |
| FR-AUTH-002 | C | A `api/auth.functional.spec.ts` · E `e2e/auth/session.functional.spec.ts` · B `auth.feature` credenciales inválidas |
| FR-AUTH-003 | C | U `test_lockout.py` · A lockout 423 |
| FR-AUTH-004 | C | A logout revoca refresh · E logout |
| FR-AUTH-005 | C | U `test_security.py` token expirado · A refresh sin cookie / revocado |
| FR-AUTH-006 | A | A recovery · E recovery UI |
| FR-AUTH-007 | A | A recovery un uso |
| FR-AUTH-008 | M | A/E perfil |
| FR-AUTH-009 | M | A activity |
| FR-AUTH-010 | C | U `test_authz.py` · A admin/support/customer · E admin redirect |

## Cuentas

| Req | Pri | Tests reales |
| --- | --- | --- |
| FR-ACCT-001 | C | A `api/accounts.functional.spec.ts` · E dashboard |
| FR-ACCT-002 | C | A campos de cuenta · seed Ana |
| FR-ACCT-003 | C | A saldos enteros · E account-balance |
| FR-ACCT-004 | C | U source blocked · A Bruno BLOCKED · E admin bloquea y submit deshabilitado |
| FR-ACCT-005 | C | A 403 cuenta ajena |
| FR-ACCT-006 | C | U `projected_available` · D `data/reconciliation.spec.ts` |

## Transferencias

| Req | Pri | Tests reales |
| --- | --- | --- |
| FR-TRF-001 | C | U `test_completes_when_funds_and_limits_allow` (mismo posting; el SUT no abre 2.ª cuenta ARS en registro). Hueco E2E propio documentado en plan Fase 4. |
| FR-TRF-002 | C | A/E transferencia a Bruno · B `transfers.feature` |
| FR-TRF-003 | C | U NSF · A/E/B fondos insuficientes |
| FR-TRF-004 | C | U per-op y daily exactos · A PER_OPERATION_LIMIT |
| FR-TRF-005 | C | U currency · A moneda USD sobre origen ARS |
| FR-TRF-006 | C | A idempotency key · B replay · D ledger sigue en 2 asientos |
| FR-TRF-007 | C | A/E/B id + status |
| FR-TRF-008 | C | U post_transfer_ledger · B/D doble asiento SQL |
| FR-TRF-009 | C | U no muta snapshots · A/B/D rechazo sin ledger |
| FR-TRF-010 | C | B/D `audit_events` vía SQL, nunca GET /audit |

## Pagos, admin, auditoría, lab

| Req | Pri | Tests reales |
| --- | --- | --- |
| FR-PAY-001 | C | U debit · A/E AYSA · D un débito ledger |
| FR-PAY-002 | A | A/E CARD/INVOICE |
| FR-PAY-003 | A | A SCHEDULED |
| FR-PAY-004 | C | I mock REJECT · A/E/D sin ledger |
| FR-PAY-005 | A | A list/get payments |
| FR-PAY-006 | C | U `test_payment_gateway.py` FakePaymentGateway; compose `PAYMENT_GATEWAY_URL=http://mocks:8090` |
| FR-ADM-001 | C | A list users + patch status |
| FR-ADM-002 | C | A/E bloqueo · D no origina |
| FR-ADM-003 | A | A operations/indicators |
| FR-ADM-004 | A | A asignar SUPPORT |
| FR-ADM-005 | C | A SUPPORT 403 mutate/transfer · E solo lectura · S `authz.spec.ts` |
| FR-ADM-006 | C | A/E CUSTOMER 403/redirect |
| FR-NTF-001 | A | Código outbox en TransferService; evidencia SQL opcional Fase 6 (outbox no afirmado aún como crítico) |
| FR-NTF-002 | A | Worker; no crítico |
| FR-NTF-003 | C | Chaos `qa/chaos/rabbit-down.sh`: transfer COMPLETED con Rabbit caído |
| FR-AUD-001 | C | D `data/transfer.ledger-audit.spec.ts` SELECT audit_events |
| FR-AUD-002 | C | D `data/audit.append-only.spec.ts` + lector sin UPDATE/INSERT |
| FR-AUD-003 | C | A smoke GET /admin/audit 404 · S también como admin |
| FR-AUD-004 | A | A operation_trace reducida |
| FR-LAB-001 | C | U `test_defects.py` flags ignorados fuera test/ci |
| FR-LAB-002 | A | Catálogo `qa/defect-lab/catalog.md` · `make qa-lab-detect` |

## NFR seguridad y a11y (Fase 7)

Leyenda extra: X a11y · S security

| Req | Pri | Tests reales |
| --- | --- | --- |
| NFR-SEC-001 | C | U `test_password_hash_is_argon2_and_not_plaintext` · S `password-storage.spec.ts` |
| NFR-SEC-002 | C | `make qa-secrets` · S `/health` no filtra secretos |
| NFR-SEC-003 | C | S endpoints 401 sin token · token basura 401 |
| NFR-SEC-004 | C | S SUPPORT 403 mutate/transfer · CUSTOMER 403 admin |
| NFR-SEC-005 | C | U JWT expirado · S cookie refresh HttpOnly + SameSite |
| NFR-SEC-006 | C | A lockout 423 (Fase 4) |
| NFR-SEC-007 | C | U headers API · S headers API + SPA · ZAP baseline |
| NFR-SEC-009 | A | `make qa-deps` (reportes, no cero CVEs inventado) |
| NFR-SEC-010 | C | ZAP solo `http://web` en Compose |
| NFR-A11Y-001 | C | X `critical-routes.spec.ts` login/cuentas/transfer/admin |
| NFR-A11Y-002 | C | X teclado en formulario de login |
| NFR-A11Y-003 | C | X skip-link + foco visible |
| NFR-A11Y-004 | C | Charter `exploratory/wcag-critical-flows.md` (axe ≠ WCAG total) |

## NFR performance, fiabilidad y datos (Fases 8–9)

Leyenda extra: P performance · C chaos · M mutation · K contract

| Req | Pri | Tests reales |
| --- | --- | --- |
| NFR-PERF-001 | C | P `login.yml` · `docs/performance/` |
| NFR-PERF-002 | C | P `accounts.yml` |
| NFR-PERF-003 | C | P `transfers.yml` (1¢, SELECT FOR UPDATE) |
| NFR-PERF-004 | C | P error rate en `qa/reports/perf/summary.json` |
| NFR-PERF-005 | A | Soak/stress no bloquean PR (política) |
| NFR-REL-002 | C | U `test_outbox_is_written_when_lab_off` · DEF-REL-001 |
| NFR-DAT-003 | C | TDM `docs/data-quality/tdm.md` · factory `uniqueCustomer` |
| NFR-ISO-002 | C | U `test_defects.py` fail-closed |

## NFR CI (Fase 10)

| Req | Pri | Tests reales |
| --- | --- | --- |
| NFR-CI-001 | C | `.github/workflows/pr.yml` lint + unit + `make qa-critical` |
| NFR-CI-002 | C | `.github/workflows/main.yml` regression + data + a11y + bdd |
| NFR-CI-003 | C | `.github/workflows/nightly.yml` a11y ya en main; nightly security/ZAP/perf/mutation |
| NFR-CI-004 | C | `scripts/ci/require-jobs.py` + job `quality-gate` (`--self-test` en lint) |

## Críticos huérfanos

Ninguno.
