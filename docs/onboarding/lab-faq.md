# FAQ del laboratorio

Decisiones del laboratorio de QA: cada respuesta apunta a un ADR o a un test ejecutable, no a un eslogan.

## Recorrido rápido

FinBank es un SUT bancario ficticio más un framework QA independiente. El valor no es el login: es poder ejercitar ledger, autorización, un lab de defectos fail-closed y un quality gate que no se puede pintar de verde.

Recorrido guiado: [demo.md](demo.md).

## Preguntas frecuentes

| Pregunta | Dónde está la respuesta |
| --- | --- |
| ¿Por qué no microservicios? | [ADR-0001](../architecture/adr/0001-modular-monolith.md) |
| ¿El saldo es la fuente de verdad? | No. Ledger sí. [ADR-0002](../architecture/adr/0002-ledger-as-source-of-truth.md) + `make qa-data` |
| ¿Por qué no hay GET `/audit`? | [ADR-0005](../architecture/adr/0005-audit-without-public-api.md). El test 404 + SQL es el DoD. |
| ¿QA importa código del SUT? | No. [ADR-0006](../architecture/adr/0006-independent-qa-framework.md) |
| ¿Y si alguien activa defectos en demo? | [ADR-0007](../architecture/adr/0007-defect-injection-isolation.md). `APP_ENV=dev` ignora flags. |
| ¿Playwright y Cucumber a la vez? | Misma `framework/`. [ADR-0009](../architecture/adr/0009-bdd-dual-runner.md) |
| ¿GitHub o GitLab? | GitHub referencia, GitLab espejo, mismos Make. [ADR-0008](../architecture/adr/0008-dual-ci.md) |
| ¿p95 de login 500 ms a 20 RPS? | No se sostuvo. Recalibrado a 10 RPS / 600 ms. [performance](../performance/budgets.md) |
| ¿Axe = WCAG? | No. [NFR-A11Y-004](../accessibility/README.md) |
| ¿Un job skipped deja el PR verde? | No. `scripts/ci/require-jobs.py` |

## Decisiones del laboratorio

1. **Dinero en enteros.** Un float en JS/Python es un defecto de diseño, no un detalle.
2. **Pirámide:** dominio en Pytest; la UI no reimplementa NSF.
3. **Factories vs seed.** Ana/Bruno solo con `@seed` o perf/chaos explícitos.
4. **Outbox, no publish en el request.** Chaos Rabbit: transfer COMPLETED igual (FR-NTF-003).
5. **Presupuestos medidos.** Bajar RPS es más honesto que inventar p95.

## Lo que este laboratorio no afirma

- “Cobertura 90 %”.
- “Mutation score X %” (solo dos mutantes de muestra, ambos KILLED).
- “ZAP limpio” (hay 6 alertas; el gate es 0 High/Critical).
- “Pipeline de GitHub verde” sin abrir el run real en [finbank-qa-lab-platform](https://github.com/mrrobotcooper-tech/finbank-qa-lab-platform/actions).
- Producto listo para un banco real.

## Cómo comprobar que el lab detecta defectos

Abrir `qa/defect-lab/catalog.md` y `apps/backend/src/finbank/domain/transfers.py` (`defect_on("DEF-FUN-001")`). Correr el detector NSF OFF y ON. Eso demuestra que la suite **falla a propósito**.
