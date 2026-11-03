# Estructura del repositorio

**Documento:** REP-001  
**Fase:** 0  
**Estado:** Aceptado (Fase 4 materializa suite funcional en `qa/automation/api` y `qa/automation/e2e`)

Monorepo. Separación estricta entre aplicación, QA, especificaciones, infraestructura y evidencias.

Los directorios de aplicación **no se materializan con código** en Fase 0. Sí se reserva el árbol documental y carpetas de contrato para que la Fase 1 no discuta layout.

```text
finbank/
├── apps/
│   ├── frontend/                 # React + Vite + TypeScript
│   └── backend/                  # FastAPI + domain + workers
├── qa/
│   ├── automation/
│   │   ├── framework/
│   │   ├── e2e/
│   │   ├── api/
│   │   ├── integration/
│   │   ├── contract/
│   │   ├── accessibility/
│   │   ├── performance/
│   │   ├── security/
│   │   ├── data/
│   │   ├── bdd/
│   │   └── exploratory/
│   ├── test-data/
│   ├── fixtures/
│   ├── mocks/
│   ├── mutations/
│   ├── chaos/
│   ├── defect-lab/
│   └── reports/                  # gitignore de artefactos generados
├── specifications/
│   ├── requirements/             # Fase 0: FR y NFR
│   ├── features/                 # Gherkin de producto (índice SDD)
│   ├── acceptance-criteria/
│   ├── test-scenarios/
│   └── traceability/
├── database/
│   ├── migrations/               # Alembic (fuente: apps/backend)
│   ├── seeds/
│   └── scripts/                  # SQL de evidencia / checks
├── infrastructure/
│   ├── docker/
│   ├── monitoring/
│   └── environments/
├── docs/
│   ├── architecture/
│   ├── qa-strategy/
│   ├── test-plans/
│   ├── test-cases/
│   ├── defect-reports/
│   ├── performance/
│   ├── security/
│   ├── accessibility/
│   ├── data-quality/
│   └── onboarding/
├── .github/workflows/
├── .gitlab-ci.yml
├── docker-compose.yml
├── Makefile
├── README.md
└── .env.example
```

## Decisiones de layout

1. **Alembic** vive en `apps/backend` como fuente. `database/migrations` puede ser un apuntador documental o un export; no se duplican revisiones.
2. **Pytest** vive en `apps/backend/tests`. QA no reescribe unit tests en TypeScript.
3. **Seeds de demo** en `database/seeds`. **Factories de test** en `qa/automation/framework` y fixtures Python de backend. No mezclar.
4. **Reports** generados no se commitean. Sí se commitean plantillas y README de cómo producirlos.
5. Un solo `docker-compose.yml` raíz con overlays en `infrastructure/environments/` (`dev`, `test`, `ci`).

## Límites de dependencia

```text
apps/frontend  →  apps/backend (HTTP)        nunca importa qa/
apps/backend   →  postgres/redis/rabbit/mocks nunca importa qa/
qa/            →  HTTP, SQL, AMQP, UI         nunca importa src de apps
specifications →  nada de runtime
infrastructure →  orquesta procesos, no reglas de negocio
```

Violar estos límites se considera defecto de arquitectura, no atajo de test.
