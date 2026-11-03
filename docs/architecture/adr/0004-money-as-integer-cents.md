# ADR-0004 — Dinero como entero de unidad menor

**Estado:** Propuesto

## Contexto

`float` en dinero es un defecto. `Decimal` JSON se serializa mal si no hay disciplina.

## Decisión

Persistencia y dominio: `bigint` en unidad menor (centavos). API: enteros + `currency`. UI: formateo en el borde. Tests comparan enteros.

No hay FX en v1. Transferencias cross-currency se rechazan.

## Consecuencias

- Data tests triviales de precisión.
- Hay que evitar `number` JS en el framework QA para importes grandes; usar `bigint` o strings decimales validados por Zod.
