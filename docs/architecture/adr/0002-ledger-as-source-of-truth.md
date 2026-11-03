# ADR-0002 — Ledger como fuente de verdad

**Estado:** Propuesto

## Contexto

Un `UPDATE accounts SET balance = balance - x` sin asiento es indemostrable y frágil en concurrencia. QA necesita reconciliar.

## Alternativas

1. Solo saldo mutable: simple, imposible de auditar bien.
2. Event sourcing puro: excesivo para el alcance.
3. **Ledger de asientos + saldo cacheado reconciliable.**

## Decisión

Toda mutación monetaria escribe `ledger_entries` en la misma transacción que actualiza `accounts.available_balance` / `held_balance`. Los data tests tratan el ledger como verdad y el saldo como proyección.

## Consecuencias

- FR-ACCT-006 y FR-TRF-008 son verificables en SQL.
- Hay que definir y congelar la fórmula de reconciliación en Fase 2.
- Tests de concurrencia (dos transferencias simultáneas) se vuelven significativos.
