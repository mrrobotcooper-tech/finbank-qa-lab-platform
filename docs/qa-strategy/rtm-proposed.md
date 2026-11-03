# Matriz de trazabilidad propuesta (RTM)

**Documento:** RTM-001  
**Fase:** 0  
**Estado:** Supersedido por la RTM viva [`specifications/traceability/rtm.md`](../../specifications/traceability/rtm.md).

Leyenda de cobertura planificada:

- U unit · I integration · A API · E E2E · B BDD · D data/SQL · S security · X a11y · P performance

Un requisito **crítico** necesita al menos un test automatizado en el nivel más cercano a la regla, más evidencia de datos si muta dinero o auditoría.

## Autenticación

| Req | AC (resumen) | U | I | A | E | B | D | S | X |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-AUTH-001 | Registro válido; email duplicado 409 | x | x | x | x | x | | x | x |
| FR-AUTH-002 | Login ok / inválido genérico | x | x | x | x | x | | x | x |
| FR-AUTH-003 | Lockout temporal | x | x | x | | x | x | x | |
| FR-AUTH-004 | Logout revoca refresh | | x | x | x | | x | x | |
| FR-AUTH-005 | Expiración y refresh | x | x | x | x | | | x | |
| FR-AUTH-006 | Recovery dispara notificación | | x | x | x | x | x | | |
| FR-AUTH-007 | Token un uso / expirado | x | x | x | | | x | x | |
| FR-AUTH-008 | Update perfil | | | x | x | | | | x |
| FR-AUTH-009 | Activity log visible | | | x | x | | x | | |
| FR-AUTH-010 | Matriz de roles | x | | x | x | x | | x | |

## Cuentas

| Req | AC (resumen) | U | I | A | E | B | D |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR-ACCT-001 | Multi-cuenta por usuario | | x | x | x | x | |
| FR-ACCT-002 | Número único, tipo, moneda, límites | x | x | x | | | x |
| FR-ACCT-003 | Saldo disponible / retenido | | x | x | x | x | x |
| FR-ACCT-004 | BLOCKED no origina | x | x | x | x | x | x |
| FR-ACCT-005 | Historial autorizado | | | x | x | | x |
| FR-ACCT-006 | Reconciliación saldo vs ledger | | x | | | | x |

FR-ACCT-006 **no** tendrá endpoint de reconciliación.

## Transferencias

| Req | AC (resumen) | U | I | A | E | B | D | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-TRF-001 | Entre propias | x | x | x | x | x | x | x |
| FR-TRF-002 | Entre clientes | x | x | x | x | x | x | |
| FR-TRF-003 | Fondos insuficientes | x | x | x | x | x | x | |
| FR-TRF-004 | Límites | x | x | x | | x | x | |
| FR-TRF-005 | Moneda distinta | x | | x | | x | | |
| FR-TRF-006 | Idempotencia | x | x | x | | | x | |
| FR-TRF-007 | ID y estado | | | x | x | x | | |
| FR-TRF-008 | Doble asiento + saldos | x | x | | | x | x | |
| FR-TRF-009 | Rechazo sin movimiento | x | x | x | | x | x | |
| FR-TRF-010 | Audit record | | x | | | x | x | |

FR-TRF-008 y FR-TRF-010 se cierran en SQL (y BDD que llama al helper SQL), no en un GET de auditoría.

## Pagos, admin, notificaciones, auditoría

| Req | Niveles mínimos | Nota de evidencia |
| --- | --- | --- |
| FR-PAY-001 | U I A E B D | Débito único en ledger |
| FR-PAY-002 | A E | |
| FR-PAY-003 | I A D | Worker de scheduled |
| FR-PAY-004 | I A D | Mock reject |
| FR-PAY-005 | A E | |
| FR-PAY-006 | I contract | Ningún host externo |
| FR-ADM-001 | A E S | |
| FR-ADM-002 | A E D | Estado en SQL |
| FR-ADM-003 | A | |
| FR-ADM-004 | A S | |
| FR-ADM-005 | A E S | SUPPORT 403 en POST transfer |
| FR-ADM-006 | A E S | |
| FR-NTF-001 | I D | Outbox |
| FR-NTF-002 | I D | notifications status |
| FR-NTF-003 | chaos D | Saldos intactos si MQ down |
| FR-AUD-001 | D | Sin API completa |
| FR-AUD-002 | D | Append-only |
| FR-AUD-003 | A S | GET completo 404 |
| FR-AUD-004 | A | Vista reducida |
| FR-LAB-001 | I S | Flags ignorados fuera test/ci |
| FR-LAB-002 | docs + tests lab | Fase 9 |

## NFR (muestra)

| Req | Cómo se verifica |
| --- | --- |
| NFR-SEC-001 | Inspección + test de que el hash no es el plaintext |
| NFR-SEC-005 | API de expiración; TTL corto en test |
| NFR-SEC-006 | API de burst login |
| NFR-A11Y-001 | axe en login, dashboard, transfer, admin — ver RTM viva |
| NFR-PERF-001–004 | Artillery; umbrales recalibrados en `docs/performance/` |
| NFR-OBS-002 | Header round-trip en API + SQL audit |
| NFR-REL-001 | Integration transaccional + data |
| NFR-CI-004 | `scripts/ci/require-jobs.py` + job `quality-gate` |

## Huecos explícitos (aceptados en Fase 0)

| Tema | Justificación |
| --- | --- |
| Reversa de transferencias | Fuera de v1 |
| FX | Fuera de v1 |
| WCAG completo manual | Checklist en Fase 7, no automatizable al 100 % |
| Soak 24 h | Nightly acotado, no PR |

Cuando un test exista, se añadirá su ID (`TC-TRF-014`, `api/transfers.idempotency.spec.ts::retry`) en una columna extra. **No se rellenará con nombres inventados ahora.**
