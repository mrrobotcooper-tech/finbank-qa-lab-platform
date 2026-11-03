# ADR-0003 — Access JWT + refresh opaco en Redis

**Estado:** Propuesto

## Contexto

Hace falta sesión revocable, expiración, lockout y tests de autorización. Las sesiones solo-JWT no se pueden invalidar en logout.

## Alternativas

| Opción | Ventaja | Costo |
| --- | --- | --- |
| JWT autosuficiente | Stateless | Logout inefectivo |
| Sesión 100 % servidor | Revocación trivial | Más acoplamiento UI |
| **JWT corto + refresh opaco en Redis** | Revocación, tests de expiración, rate limit colocalizado | Dos artefactos que gobernar |

## Decisión

- Access: JWT 15 min, en memoria del SPA (no `localStorage`).
- Refresh: cookie HttpOnly + SameSite, valor opaco hasheado en Redis.
- Lockout y rate limit en Redis.
- CSRF: SameSite estricto; operaciones de dinero también exigen Bearer.

## Consecuencias

- Chaos de Redis impacta login y refresh: escenario de laboratorio válido.
- E2E de sesión expirada es implementable de verdad (no un timeout fingido).
- Hay que documentar el clock de tests (no depender del sleep de 15 min: fixture de TTL corto en `test`).
