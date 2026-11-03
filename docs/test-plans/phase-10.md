# Plan táctico — Fase 10 CI/CD

**DoD:** un fallo de test crítico pone la pipeline en rojo. Documentado.

## Alcance

| Pieza | Dónde |
| --- | --- |
| PR | `.github/workflows/pr.yml` |
| main | `.github/workflows/main.yml` |
| nightly | `.github/workflows/nightly.yml` |
| GitLab espejo | `.gitlab-ci.yml` |
| Scripts | `scripts/ci/` + Make (`qa-critical`) |
| Gates | `docs/ci/quality-gates.md` |

GitHub es la ejecución de referencia. GitLab replica etapas y gates (ADR-0008).

## Cómo correr en local

```bash
python3 scripts/ci/require-jobs.py --self-test
make lint && make typecheck && make test
make qa-secrets
make qa-critical
```

Firefox/WebKit: `QA_BROWSERS=full make qa-smoke` (nightly, no PR).

## Verificación (2026-11-03)

- `require-jobs.py --self-test` OK. Mock `unit=failure` → exit 1; todos `success` → exit 0.
- Pytest 77 + JUnit `qa/reports/junit-pytest.xml` + Allure results.
- Vitest 10. QA lint/tsc OK. GitHub/GitLab YAML parseable.
- `make qa-secrets` OK (`.env` no versionado).
- `qa-deps` no es gate.
