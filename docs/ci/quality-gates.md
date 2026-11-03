# Quality gates — NFR-CI-004

**Documento:** CI-001  
**Fase:** 10

Un job **crítico** en `failure`, `skipped` o `cancelled` deja la pipeline en rojo. No hay `continue-on-error` / `allow_failure` en esos jobs.

## Jobs críticos

| Pipeline | Jobs que el gate exige en `success` |
| --- | --- |
| PR / merge request | `lint-typecheck`, `unit`, `secrets`, `qa-critical` |
| `main` | los de PR sustituyendo smoke por `qa-regression`, más `qa-data`, `qa-a11y`, `qa-bdd` |
| Nightly | `qa-security`, `qa-zap`, `qa-browsers`, `qa-perf`, `qa-advanced` (GitHub). GitLab schedule: `qa-security` + `qa-zap`. |

`qa-deps` es **informativo** (`continue-on-error: true` / no entra al gate): el audit de `qa/` tiene un high transitivo en `zod` documentado en Fase 7.

## Cómo se implementa

- GitHub: job `quality-gate` con `if: always()` y `python3 scripts/ci/require-jobs.py` sobre `${{ toJson(needs) }}`.
- GitLab: `needs:` sin `optional` y sin `allow_failure`. Si un need falla, el gate no corre y la pipeline queda failed.

```bash
python3 scripts/ci/require-jobs.py --self-test
```

## Artefactos

JUnit (`qa/reports/junit.xml`, `junit-pytest.xml`, `cucumber-junit.xml`) y Allure results (`qa/reports/allure-results`). HTML Allure local:

```bash
npx --prefix qa --yes allure generate qa/reports/allure-results -o qa/reports/allure --clean
```
