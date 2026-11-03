# Estrategia de testing — FinBank

**Documento:** QAS-001  
**Fase:** 0  
**Estado:** En revisión  
**Alcance:** estrategia inicial; los test plans tácticos se escriben al entrar a cada fase de ejecución.

## 1. Objetivos

1. Proteger las reglas de dinero, identidad y autorización.
2. Hacer visible la calidad del producto, de la suite y del proceso, por separado.
3. Permitir que un requisito se verifique aunque no tenga API.
4. Detectar defectos intencionales del lab.
5. No mentir con pipelines verdes.

## 2. Principios

- **Pirámide honesta:** el dominio se prueba en Pytest; la UI no reimplementa reglas.
- **Independencia:** cero estado compartido accidental.
- **Evidencia:** cada fallo crítico deja log, correlation ID y, si aplica, SQL.
- **No testear al mock:** los mocks aíslan terceros, no al SUT en el camino crítico.
- **Axe ≠ WCAG:** la a11y automática es red, no cierre.
- **Cobertura de líneas ≠ cobertura funcional.** La RTM manda sobre el porcentaje de pytest.

## 3. Niveles

| Nivel | Dónde | Qué demuestra | Cuándo |
| --- | --- | --- | --- |
| Unit | `apps/backend/tests/unit` | Límites, estados, idempotencia, authz pura | PR |
| Unit UI | `apps/frontend` Vitest | Formatters, validación de forms | PR |
| Integration | `apps/backend/tests/integration` | SQLAlchemy, Redis, transacción, outbox | PR |
| API | `qa/automation/api` | Contratos, authz, errores, Zod | PR smoke / main full |
| Contract | `qa/automation/contract` | Pact consumer/provider | main |
| Data | `qa/automation/data` | Integridad, reconciliación, audit sin API | main / nightly |
| E2E | `qa/automation/e2e` | Flujos de usuario, roles, sesión | PR critical / main |
| BDD | `qa/automation/bdd` | Aceptación Gherkin | main |
| A11y | `qa/automation/accessibility` | axe + teclado en rutas críticas | main / nightly |
| Security | `qa/automation/security` | OWASP checks defensivos, ZAP local | nightly |
| Performance | `qa/automation/performance` | Load/spike/soak en lab | nightly / manual |
| Chaos | `qa/chaos` | Redis/PG/Rabbit/mocks down | manual / nightly acotado |
| Mutation | `qa/mutations` | Calidad de tests de dominio | nightly sample |
| Exploratory | `qa/automation/exploratory` | Charters, riesgo, no automatizable | manual |

## 4. Clasificación de suites

Smoke, sanity, regression, functional, integration, critical path, exploratory. Cada spec lleva tags. El Makefile y CI filtran por tag, no por copiar carpetas.

## 5. Datos

- Factories sintéticas, emails `qa+{uuid}@finbank.test`.
- Seeds solo para demo y tests `@seed`.
- Isolation por fila única; cleanup por prefijo.
- Perfiles: `happy`, `zero-balance`, `near-limit`, `blocked-account`, `locked-user`.

## 6. Ambientes de prueba

Compose `test`: TTL de token corto, mocks deterministas, defect flags off por defecto. Lab compose: flags on según catálogo. Nunca internet de terceros.

## 7. Criterios de entrada y salida (genéricos)

### Entrada a un ciclo de ejecución

- Artefacto desplegable en compose healthy.
- Migraciones aplicadas.
- Flags de defecto conocidos.
- RTM del incremento actualizada.

### Salida

- Cero defectos críticos abiertos en el incremento.
- Smoke verde.
- Requisitos críticos del incremento: pass o hueco justificado.
- Reportes publicados (JUnit/Allure en artefactos de CI).

Criterios tácticos por fase se añaden en `docs/test-plans/`.

## 8. Manejo de defectos

Severidad: blocker / critical / major / minor / cosmetic.  
Prioridad: P0–P3.  
Un fallo de integridad de ledger o de authz es P0.  
Flaky tests se quarantinan con issue; no se silencian con retry infinito. Retry de Playwright: 1 en CI para UI, 0 para API/data.

## 9. Riesgos de producto vs de suite

| Riesgo de producto | Mitigación de test |
| --- | --- |
| Doble gasto | Idempotencia + unique SQL + E2E de retry |
| Escalada de privilegios | API authz matrix + E2E negativo |
| Saldo divergente | Data reconciliation |
| Sesión zombi | Logout + Redis revoke |
| Pago aprobado y no debitado | Integration mock + ledger |

| Riesgo de suite | Mitigación |
| --- | --- |
| Tests acoplados al seed | Factories |
| Selectores frágiles | `data-testid` |
| Falsos verdes | Quality gates, mutation sample, defect lab |
| Tiempo de CI | Pirámide y tags |

## 10. Herramientas (cerradas en Fase 0)

| Uso | Herramienta | Alternativa rechazada |
| --- | --- | --- |
| E2E / API HTTP | Playwright Test | Cypress (menos API/a11y unificada) |
| BDD | Cucumber + Playwright | Solo comentarios Gherkin |
| Schemas TS | Zod | JSON Schema suelto |
| Unit backend | Pytest | unittest |
| Performance | Artillery | k6 (válido; Artillery pedido) |
| A11y | axe-core | Lighthouse solo |
| Contratos | Pact | Solo Zod (no consumer/provider) |
| Reportes | Allure + JUnit | HTML único |
| Security lab | checks propios + ZAP local | scans a terceros |
| Mutation | mutmut (Py) + Stryker (TS) | ninguna en v0 |

## 11. Trazabilidad

Requirement → Specification → Acceptance criteria → Scenario → Automated test → Result → Evidence.

Implementación de matriz: [rtm.md](../../specifications/traceability/rtm.md) (IDs reales). Propuesta inicial: [rtm-proposed.md](rtm-proposed.md).

## 12. Lo que esta estrategia no cubre aún

- Heurísticas detalladas de cada charter exploratorio (Fase 9).
- Presupuestos de performance calibrados (Fase 8).
- Catálogo de defectos (Fase 9).
- Números de cobertura: no existen hasta que hay código.
