# FinBank QA

Framework de Quality Engineering **independiente del SUT**. Habla HTTP y UI. No importa código de `apps/`.

Demo y evidencia de cierre: [docs/onboarding/demo.md](../docs/onboarding/demo.md), [docs/evidence/2026-11-03.md](../docs/evidence/2026-11-03.md).

## Fases 8–9 — performance y advanced

- Artillery en el host (`make qa-perf`)
- Defect lab fail-closed (`make qa-lab-detect`)
- Pact muestra GET `/health` (`make qa-pact`)
- Mutation sample (`make qa-mutate`)
- Chaos Redis/Rabbit en el host (`make qa-chaos`)
- TDM: `docs/data-quality/tdm.md`
- Charters: `qa/automation/exploratory/`

## Fase 7 — a11y y security

- Axe + teclado (`make qa-a11y`)
- Authz/headers/Argon2 (`make qa-security`)
- ZAP baseline local (`make qa-zap`)
- Dependencias y `.env` (`make qa-deps`, `make qa-secrets`)

## Fases 5–6 — BDD y datos

- Cucumber sobre `framework/` (`make qa-bdd`)
- SQL `finbank_qa_reader` (`make qa-data`)
- RTM: `specifications/traceability/rtm.md`

## Fase 4 — funcional

Happy/negative/edge en API y E2E Chromium. Tags `@smoke` `@regression` `@critical`.

## Fase 3 — núcleo

- Playwright Test (API + E2E Chromium)
- Clientes HTTP + Zod
- Fixtures de rol y factory de clientes únicos
- POM de login, registro y cuentas
- Smoke real contra Compose (`@smoke`)

```bash
# con el stack levantado
cd qa && npm ci && npx playwright install chromium
QA_BASE_URL=http://localhost:5173 QA_API_URL=http://localhost:8000 npm run test:smoke

make qa-smoke
make qa-regression
make qa-bdd
make qa-data
make qa-a11y
make qa-security
make qa-zap
make qa-deps
make qa-secrets
make qa-perf
make qa-lab-detect
make qa-pact
make qa-mutate
make qa-chaos
```

## Fase 10 — CI

`make qa-critical` es el gate de PR (API smoke + E2E Chromium `@smoke|@critical`). Workflows: `.github/workflows/`. Espejo: `.gitlab-ci.yml`.

Reports locales: `qa/reports/` (gitignored). JUnit + Allure results se suben como artefactos.
