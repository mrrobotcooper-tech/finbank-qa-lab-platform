# language: es
@bdd @critical @transfers
Característica: Transferencias entre clientes
  Como titular CUSTOMER
  Quiero transferir centavos enteros
  Para mover saldo entre cuentas activas de la misma moneda

  @FR-TRF-002 @FR-TRF-007 @FR-TRF-008 @FR-TRF-010
  Escenario: transferencia fondeada a Bruno queda COMPLETED con doble asiento
    Dado un cliente de laboratorio fondeado con 430 centavos
    Cuando transfiere 430 centavos a la cuenta corriente de Bruno
    Entonces la transferencia queda "COMPLETED"
    Y su saldo disponible es 0
    Y el ledger tiene débito y crédito por 430 centavos
    Y existe un evento de auditoría transfer.created sin usar GET de auditoría

  @FR-TRF-003 @FR-TRF-009
  Escenario: fondos insuficientes rechazan sin movimiento
    Dado un cliente ya registrado
    Cuando transfiere 500 centavos a la cuenta corriente de Bruno
    Entonces la transferencia queda "REJECTED"
    Y el motivo de rechazo es "INSUFFICIENT_FUNDS"
    Y el ledger de esa operación está vacío

  @FR-TRF-006
  Escenario: la misma Idempotency-Key no duplica el movimiento
    Dado un cliente de laboratorio fondeado con 250 centavos
    Cuando transfiere 250 centavos a Bruno dos veces con la misma clave de idempotencia
    Entonces ambas respuestas comparten el mismo identificador
    Y el ledger de esa operación tiene exactamente 2 asientos
