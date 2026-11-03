# Requisitos funcionales — FinBank

**Documento:** REQ-FUN-001  
**Fase:** 0  
**Estado:** Baseline versionado (Fase 5). Trazas reales en `specifications/traceability/rtm.md`.

Los IDs de esta lista son la clave primaria de la [matriz de trazabilidad](../../docs/qa-strategy/rtm-proposed.md). Un requisito crítico no puede quedar sin test ni sin justificación de hueco.

Prioridad: **C** crítico · **A** alto · **M** medio.

## Autenticación y usuarios

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-AUTH-001 | Un usuario puede registrarse con email único, contraseña que cumple política, y datos personales mínimos. | C |
| FR-AUTH-002 | El sistema autentica credenciales válidas y rechaza las inválidas sin revelar cuál campo falló. | C |
| FR-AUTH-003 | Tras N intentos fallidos consecutivos, la cuenta se bloquea temporalmente. | C |
| FR-AUTH-004 | El usuario puede cerrar sesión y el refresh token queda revocado. | C |
| FR-AUTH-005 | El access token expira; un refresh válido emite uno nuevo; uno revocado o vencido no. | C |
| FR-AUTH-006 | Un usuario puede iniciar recuperación de contraseña simulada. | A |
| FR-AUTH-007 | El token de recovery expira y es de un solo uso. | A |
| FR-AUTH-008 | El perfil muestra y permite actualizar datos personales no sensibles de autenticación. | M |
| FR-AUTH-009 | Existe historial de actividad de autenticación y operaciones de cuenta visibles al titular. | M |
| FR-AUTH-010 | Los roles CUSTOMER, SUPPORT y ADMIN tienen permisos distintos, enforceados en API y UI. | C |

## Cuentas

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-ACCT-001 | Un CUSTOMER puede tener una o más cuentas. | C |
| FR-ACCT-002 | Cada cuenta tiene número único, tipo, moneda, estado y límites. | C |
| FR-ACCT-003 | El saldo disponible y el retenido son consultables. | C |
| FR-ACCT-004 | Una cuenta BLOCKED no origina transferencias ni pagos. | C |
| FR-ACCT-005 | El historial de movimientos pertenece solo a cuentas existentes y al titular o a roles autorizados. | C |
| FR-ACCT-006 | El saldo persistido es reconciliable contra el ledger de movimientos. | C |

## Transferencias

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-TRF-001 | Un CUSTOMER puede transferir entre cuentas propias activas de la misma moneda. | C |
| FR-TRF-002 | Un CUSTOMER puede transferir a una cuenta de otro cliente activa, misma moneda. | C |
| FR-TRF-003 | Una transferencia se rechaza si el saldo disponible es insuficiente. | C |
| FR-TRF-004 | Una transferencia se rechaza si excede el límite por operación o el acumulado diario. | C |
| FR-TRF-005 | Una transferencia se rechaza si las monedas no coinciden. | C |
| FR-TRF-006 | Reintentos con la misma Idempotency-Key no duplican el movimiento. | C |
| FR-TRF-007 | Toda transferencia tiene identificador único y estado explícito. | C |
| FR-TRF-008 | Una transferencia COMPLETED genera exactamente dos asientos de ledger (débito y crédito) y actualiza ambos saldos. | C |
| FR-TRF-009 | Una transferencia REJECTED o FAILED no altera saldos. | C |
| FR-TRF-010 | Toda transferencia COMPLETED genera un registro de auditoría. | C |

## Pagos

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-PAY-001 | Un CUSTOMER puede pagar un servicio ficticio debitando una cuenta propia activa. | C |
| FR-PAY-002 | Un CUSTOMER puede registrar un pago de factura o tarjeta ficticio. | A |
| FR-PAY-003 | Un CUSTOMER puede programar un pago futuro. | A |
| FR-PAY-004 | Un pago rechazado por la pasarela mock no debita el ledger. | C |
| FR-PAY-005 | Los pagos tienen historial y estado visible para el titular. | A |
| FR-PAY-006 | La pasarela de pagos es sustituible por mock/stub; no hay llamadas a adquirentes reales. | C |

## Administración

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-ADM-001 | ADMIN puede listar usuarios y cambiar estado (activo, bloqueado, deshabilitado). | C |
| FR-ADM-002 | ADMIN puede bloquear y desbloquear cuentas. | C |
| FR-ADM-003 | ADMIN puede consultar operaciones y ver indicadores agregados. | A |
| FR-ADM-004 | ADMIN puede asignar roles. | A |
| FR-ADM-005 | SUPPORT puede consultar, no mutar dinero ni roles. | C |
| FR-ADM-006 | CUSTOMER no accede a rutas ni endpoints de administración. | C |

## Notificaciones

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-NTF-001 | Login, transferencia y pago publican un evento de notificación. | A |
| FR-NTF-002 | El worker persiste el intento de envío y su resultado. | A |
| FR-NTF-003 | Si RabbitMQ no está disponible, la operación de negocio no se corrompe; el fallo queda observable. | C |

## Auditoría

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-AUD-001 | Cada mutación relevante registra actor, acción, entidad, before, after, correlation ID y timestamp. | C |
| FR-AUD-002 | Los registros de auditoría son append-only. | C |
| FR-AUD-003 | No existe un endpoint público que exponga el historial completo de auditoría. | C |
| FR-AUD-004 | ADMIN puede consultar una vista operativa limitada, insuficiente para sustituir FR-AUD-001 en tests de datos. | A |

## Defect Injection Lab (producto)

| ID | Requisito | Pri |
| --- | --- | --- |
| FR-LAB-001 | Los defectos intencionales solo pueden activarse en perfiles `test` o `ci`. | C |
| FR-LAB-002 | Cada defecto tiene ID, test detector y evidencia en catálogo. | A |
