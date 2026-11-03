# Test Data Management — FinBank

**Documento:** TDM-001  
**Fase:** 9

## Principios

1. Datos **ficticios**. Dominio `@finbank.test`. Nada de PII real.
2. Cada test posee su ciclo de vida. Factories con UUID, no estado compartido entre workers.
3. El seed de demo (Ana, Bruno, Cara, admin, support) solo se afirma con tag `@seed` o en performance/chaos explícitos.
4. El lector SQL `finbank_qa_reader` es SELECT-only (ADR-0005 / Fase 6).
5. Importes en enteros de centavos. Nunca `float`.

## Perfiles

| Perfil | Origen | Uso |
| --- | --- | --- |
| Seed demo | `finbank.seed` / init SQL | UI demo, `@seed`, Artillery (Ana), chaos |
| Factory HTTP | `qa/automation/framework/factory.ts` `uniqueCustomer()` | API/E2E/BDD |
| Fondeo | transferencia 1¢–N desde Ana | clientes únicos sin afirmar el saldo residual de Ana |
| Lector SQL | `QA_DATABASE_URL` | data tests, nunca DML |

Contraseña de cliente de factory: `Customer1!` (`CUSTOMER_PASSWORD`).

## Semillas demo (no mutar salvo tests `@seed`)

| Usuario | Rol | CBU relevante |
| --- | --- | --- |
| ana@finbank.test | CUSTOMER | checking ARS `32200000000000000001` |
| bruno@finbank.test | CUSTOMER | checking `32200000000000000003` (destino) |
| cara@finbank.test | CUSTOMER | checking sin saldo |
| support@finbank.test | SUPPORT | solo lectura |
| admin@finbank.test | ADMIN | bloqueo de cuentas |

`PER_OPERATION_LIMIT = 5_000_000`. `LOGIN_MAX_ATTEMPTS = 5`.

## Retención y limpieza

- Compose: volúmenes locales. Reset: `docker compose down -v`.
- Tests: entidades `qa+{uuid}@finbank.test`. No hay job de purge en v1; el volumen de lab se recrea.
- Performance: POST de 1 centavo desde Ana. No se reconcilia el saldo de Ana después.
- Defect lab: no persiste flags; `APP_ENV=dev` ignora el header.

## Trazabilidad

Factories y seeds cubren NFR-DAT-003. Evidencia SQL: `make qa-data`.
