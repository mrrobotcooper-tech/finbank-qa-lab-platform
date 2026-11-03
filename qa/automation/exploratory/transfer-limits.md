# Charter — límites de transferencia

**ID:** EXP-TRF-001  
**Tiempo:** 45 min  
**Misión:** explorar NSF, tope por operación y tope diario en UI y API.

## Cuentas

- Ana (saldo alto ARS)
- Cara (saldo 0)
- Bruno checking como destino `32200000000000000003`

## Ideas

- Importe 0, negativo, no numérico, más de 2 decimales
- Exactamente `PER_OPERATION_LIMIT` vs +1 centavo
- Replay con la misma `Idempotency-Key`
- Destino igual al origen (si el SUT lo permite en UI)
- Cuenta bloqueada de Bruno como origen

## Notas de sesión

_(completar en la sesión; no convertir todo hallazgo en automatización)_
