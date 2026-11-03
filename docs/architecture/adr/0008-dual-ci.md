# ADR-0008 — GitHub Actions primario, GitLab CI portable

**Estado:** Aceptado

## Contexto

El laboratorio debe poder ejecutarse en ambas plataformas sin mantener dos verdades de negocio.

## Decisión

GitHub Actions es la ejecución de referencia (PRs reales). `.gitlab-ci.yml` replica las mismas etapas y quality gates. La lógica compartida se documenta en `docs/` y, cuando sea posible, en scripts `Makefile`/`scripts/ci/` invocados por ambos.

## Decisión de calidad de pipeline

- PR: lint, typecheck, unit, API smoke, E2E critical path (Chromium).
- `main`: regresión más ancha + a11y smoke + data smoke.
- Nightly: browsers extra, Artillery smoke, security, mutation sample.
- Fail-fast en jobs críticos; jobs costosos `continue-on-error: false` cuando son quality gates, `true` solo en jobs informativos explícitos.

## Consecuencias

- Hay que evitar copiar YAML a mano sin scripts.
- Un pipeline verde con un job crítico skipped se considera defecto de CI.
