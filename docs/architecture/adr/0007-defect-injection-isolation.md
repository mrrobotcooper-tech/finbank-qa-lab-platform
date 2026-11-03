# ADR-0007 — Defect Injection Lab aislado

**Estado:** Aceptado

## Contexto

Los defectos intencionales demuestran que la suite detecta problemas reales. Si se activan por error, invalidan el producto y el laboratorio.

## Decisión

- Flags leídos únicamente si `APP_ENV` es `test` o `ci`.
- En cualquier otro valor, el módulo de defectos es un no-op y un log de intento es un error.
- Activación por `FINBANK_DEFECTS=DEF-004,DEF-011` y/o header `X-Finbank-Defects` aceptado solo en esos ambientes.
- Catálogo versionado en `qa/defect-lab/`.

## Consecuencias

- Tests del lab son duales: defecto OFF (pass) y ON (fail esperado / aserción de detección).
- Compose de lab separado del de demo.
