# ADR-0006 — Framework QA independiente

**Estado:** Propuesto

## Contexto

Si los tests importan módulos de la app, dejan de ser pruebas de sistema y se vuelven tests blancos disfrazados.

## Decisión

`qa/` es un proyecto TypeScript propio. Habla HTTP, UI, SQL y AMQP. Pytest colocalizado cubre unidad/integración del backend. Ningún import cruzado `qa` ↔ `apps`.

## Consecuencias

- Duplicación consciente de tipos vía Zod vs Pydantic; Pact reduce el drift.
- El contrato de `data-testid` y de APIs se vuelve API pública de testing.
- CI orquesta dos toolchains (Python y Node).
