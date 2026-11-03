# Charter — outbox y notificaciones

**ID:** EXP-NTF-001  
**Tiempo:** 35 min  
**Misión:** una transferencia COMPLETED deja rastro de notificación sin API de auditoría.

## Ideas

- SQL `outbox_events` / `notifications` como `finbank_qa_reader`
- Worker caído: el outbox queda pending
- Chaos Rabbit (`make qa-chaos`): COMPLETED igual
- UI de notificaciones de Ana tras una transfer

## Notas de sesión

_(sesión)_
