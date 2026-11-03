# Casos Fase 4 — IDs reales

Las filas apuntan a specs ejecutables. No hay placeholders.

| ID | Req | Spec |
| --- | --- | --- |
| TC-AUTH-409 | FR-AUTH-001 | `api/auth.functional.spec.ts` email duplicado |
| TC-AUTH-WEAK | FR-AUTH-001 | `api/auth.functional.spec.ts` contraseña débil |
| TC-AUTH-GENERIC | FR-AUTH-002 | `api/auth.functional.spec.ts` + `e2e/auth/session.functional.spec.ts` |
| TC-AUTH-LOCK | FR-AUTH-003 | `api/auth.functional.spec.ts` lockout 423 |
| TC-AUTH-LOGOUT | FR-AUTH-004 | `api/auth.functional.spec.ts` + E2E logout |
| TC-AUTH-REFRESH | FR-AUTH-005 | `api/auth.functional.spec.ts` refresh sin cookie / revocado |
| TC-AUTH-RECOVERY | FR-AUTH-006/007 | `api/auth.functional.spec.ts` recovery un uso + E2E aviso |
| TC-AUTH-PROFILE | FR-AUTH-008/009 | API perfil/actividad + E2E perfil |
| TC-ACCT-OWN | FR-ACCT-001/002/003 | `api/accounts.functional.spec.ts` |
| TC-ACCT-AUTHZ | FR-ACCT-005 | cuenta de otro → 403 |
| TC-TRF-PEER | FR-TRF-002/007 | API + E2E transferencia a Bruno |
| TC-TRF-NSF | FR-TRF-003/009 | API + E2E INSUFFICIENT_FUNDS |
| TC-TRF-IDEM | FR-TRF-006 | misma Idempotency-Key |
| TC-TRF-FX | FR-TRF-005 | ARS → USD seed |
| TC-TRF-LIMIT | FR-TRF-004 | PER_OPERATION_LIMIT |
| TC-TRF-BLOCK | FR-ACCT-004 | Bruno BLOCKED + admin block |
| TC-PAY-OK | FR-PAY-001/002/005 | AYSA COMPLETED API+E2E |
| TC-PAY-REJECT | FR-PAY-004 | payee REJECT |
| TC-PAY-SCHED | FR-PAY-003 | SCHEDULED sin débito |
| TC-ADM-LIST | FR-ADM-001/003 | indicadores y usuarios |
| TC-ADM-BLOCK | FR-ADM-002 | bloqueo UI+API |
| TC-ADM-SUPPORT | FR-ADM-005 | SUPPORT 403 mutate |
| TC-ADM-CUSTOMER | FR-ADM-006 | CUSTOMER 403 / redirect |
| TC-AUD-404 | FR-AUD-003 | smoke `GET /admin/audit` 404 |
