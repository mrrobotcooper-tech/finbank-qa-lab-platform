# Arquitectura del framework QA

**Documento:** QAF-001  
**Fase:** 10  
**Estado:** Núcleo + funcional + Cucumber + data SQL + axe + security + Artillery + defect lab + Pact + chaos + CI dual.

El framework QA es un **producto interno independiente** de FinBank. Consume el SUT por HTTP, UI, SQL y, cuando haga falta, AMQP. No importa código Python de la aplicación. Ver [ADR-0006](adr/0006-independent-qa-framework.md).

## 1. Mapa de módulos

```text
qa/
├── automation/
│   ├── framework/          # núcleo Playwright + clientes + fixtures
│   ├── e2e/                # UI flows (Playwright Test)
│   ├── api/                # contratos HTTP + Zod
│   ├── integration/        # API + DB + mocks
│   ├── contract/           # Pact consumer/provider
│   ├── accessibility/      # axe-core + notas WCAG
│   ├── performance/        # Artillery
│   ├── security/           # authz, headers, ZAP local
│   ├── data/               # SQL, reconciliación, sin API
│   ├── bdd/                # Cucumber + Gherkin ejecutable
│   └── exploratory/        # charters (proceso, no suite)
├── test-data/              # perfiles, datasets versionados
├── fixtures/               # payloads y estados reutilizables
├── mocks/                  # definiciones WireMock / contratos mock
├── mutations/              # config mutmut / Stryker
├── chaos/                  # escenarios compose
├── defect-lab/             # catálogo y matriz de detección
└── reports/                # salida local gitignored + README
```

Los tests **unitarios e de integración de backend** viven en `apps/backend/tests/` (TDD colocalizado). No se duplican en `qa/`.

## 2. Núcleo (`qa/automation/framework`)

Responsabilidades reales, sin capas de adorno:

| Pieza | Función |
| --- | --- |
| `config` | Ambiente, URLs, timeouts, tags, desde env |
| `fixtures` | Browser, usuario por rol, API autenticada, DB pool |
| `pages` | Page Object Model por flujo, selectores `data-testid` |
| `api-clients` | Un cliente por dominio (auth, accounts, transfers, payments, admin) |
| `auth` | Login API + inyección de sesión en UI |
| `data-factory` | Builders HTTP/SQL de usuarios, cuentas, saldos |
| `sql` | Assertions y queries de evidencia |
| `assertions` | Custom matchers de dinero, estados, correlation ID |
| `reporting` | Allure, screenshots, traces, SQL dumps acotados |

Convenciones:

- Tests independientes; ningún `test.beforeAll` comparte entidades mutables entre workers.
- Nombres: `dominio/accion.spec.ts`, tags `@smoke @critical @customer`.
- Selectores: `data-testid` estables. Prohibido xpath absoluto.
- Dinero: comparar enteros o decimal serializado, nunca floats JS.

## 3. Dos runners TypeScript, una sola librería

| Runner | Uso |
| --- | --- |
| Playwright Test | E2E, API, a11y, integration TS, security checks HTTP |
| Cucumber (`@cucumber/cucumber`) | Features Gherkin de aceptación (SDD/BDD) |

Ambos importan `framework`. Cucumber no reimplementa clientes. Ver [ADR-0009](adr/0009-bdd-dual-runner.md).

Gherkin vive en `qa/automation/bdd/features/` **y** se espeja o referencia desde `specifications/features/` para SDD. Una sola fuente ejecutable: `qa/automation/bdd/features`. Las specs en `specifications/` apuntan a esas features por ruta.

## 4. Pirámide y propiedad

```text
Exploratory / Chaos / Soak          (manual o nightly, no PR)
Performance Artillery               (nightly + smoke acotado)
E2E UI Playwright                   (critical path en PR, full en main)
BDD Cucumber                        (aceptación de dominio en main)
API + Contract + Data SQL           (PR para smoke/críticos)
Integration backend Pytest          (PR)
Unit domain Pytest + frontend Vitest(PR, rápidos)
```

Vitest cubre utilidades de UI, no sustituye E2E.

## 5. Clientes API y contratos

Cada cliente:

1. Construye request tipado.
2. Adjunta `Authorization`, `X-Correlation-ID`, `Idempotency-Key`.
3. Valida response con **Zod**.
4. Expone el body crudo para tests negativos (Zod se aplica cuando el contrato debe cumplirse).

Pact (Fase 9) genera contratos consumer desde `qa/automation/contract` y el provider se verifica contra `finbank-api`.

## 6. Data testing (prioridad)

El módulo `qa/automation/data` tiene conexión PostgreSQL propia (rol `finbank_qa_reader`).

Patrón obligatorio para requisitos sin API:

```text
Arrange  factory crea actores y cuentas
Act      API o UI ejecuta la operación
Assert   SQL sobre ledger / audit / outbox
Evidence se adjunta al reporte (query + recorte de filas)
```

No se creará un endpoint “para que el test sea más fácil” si el requisito de producto dice que no existe.

## 7. Aislamiento y datos

- Factories generan identidades únicas por test.
- Cleanup: delete por `email`/`id` prefix `qa+` o transacciones donde el test posee el ciclo de vida.
- Prohibido depender del seed de demo salvo tests de demo explícitamente taggeados `@seed`.
- Parallelismo Playwright habilitado; la idempotency key incluye `testId` + UUID.

## 8. Defect Injection Lab

Flags leídos solo si `APP_ENV` ∈ {`test`,`ci`}. El framework activa un defecto vía header interno de test o env del compose de lab, nunca vía UI de producción. Catálogo en `qa/defect-lab/catalog.md` (Fase 9). Cada defecto declara el test que **debe fallar** cuando está ON y pasar cuando está OFF.

## 9. Reporting y métricas

| Artefacto | Origen |
| --- | --- |
| Allure | Playwright, Cucumber, Pytest |
| JUnit XML | CI |
| HTML Playwright | UI |
| Artillery JSON/HTML | Performance |
| axe reports | Accessibility |
| SQL evidence | Data |
| ZAP/dependency | Security |

Métricas de proceso: [docs/evidence/2026-11-03.md](../evidence/2026-11-03.md). No hay mutation score porcentual (solo dos mutantes KILLED). Flakes no se midieron en un nightly largo.

## 10. Lo que el framework no hará

- Tests vacíos o `expect(true).toBeTruthy()`.
- Dormir `waitForTimeout` como sincronización primaria.
- Mockear el backend entero en los E2E de camino crítico (sí se mockean terceros).
- Tratar cobertura de líneas como cobertura funcional.
