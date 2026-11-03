# ADR-0009 — Playwright Test y Cucumber

**Estado:** Propuesto

## Contexto

Playwright Test es el mejor runner para E2E/API/a11y. El relato BDD Senior exige Gherkin ejecutable, no comentarios encima de un `test()`.

`playwright-bdd` unifica runners pero acopla el estilo Gherkin al de Playwright y es menos reconocible como “Cucumber” en entrevistas.

## Alternativas

1. Solo Playwright Test + features no ejecutables: SDD débil.
2. Solo Cucumber: peor DX para traces, fixtures y a11y.
3. **Playwright Test para ingeniería de tests + Cucumber para aceptación de dominio, ambos sobre `framework/`.**

## Decisión

Opción 3. Las features de aceptación de transfers, auth, payments, accounts y admin corren en Cucumber. El resto (responsive, a11y, API schema, data SQL) no se traduce a Gherkin a la fuerza.

## Consecuencias

- Dos comandos de test TS.
- Steps específicos de dominio; prohibido `When I click "{string}"` genérico como estilo dominante.
- CI debe fallar si cualquiera de los dos runners críticos falla.
