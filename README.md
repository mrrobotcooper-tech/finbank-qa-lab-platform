# FinBank — QA Engineering Platform

Banco digital **ficticio** + plataforma de Quality Assurance de nivel Senior. No procesa dinero real ni PII real. El SUT existe para que las pruebas importen: ledger, authz, datos sin API, lab de defectos y un pipeline que no se puede pintar de verde.

> **Fases 0–11 cerradas en local el 2026-11-03.**  
> Repo: [mrrobotcooper-tech/finbank-qa-lab-platform](https://github.com/mrrobotcooper-tech/finbank-qa-lab-platform)  
> Demo: [docs/onboarding/demo.md](docs/onboarding/demo.md) · Evidencia: [docs/evidence/2026-11-03.md](docs/evidence/2026-11-03.md) · Entrevista: [docs/onboarding/interview-guide.md](docs/onboarding/interview-guide.md)

## Arranque

```bash
git clone https://github.com/mrrobotcooper-tech/finbank-qa-lab-platform.git
cd finbank-qa-lab-platform
cp .env.example .env
make up
make ready
```

| Superficie | URL |
| --- | --- |
| Web | http://localhost:5173 |
| API | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| RabbitMQ UI | http://localhost:25673 |

| Usuario | Clave | Rol |
| --- | --- | --- |
| ana@finbank.test | Customer1! | Cliente (saldo ARS/USD) |
| bruno@finbank.test | Customer1! | Destino CBU `32200000000000000003` |
| support@finbank.test | SupportPassw0rd | Solo lectura |
| admin@finbank.test | AdminPassw0rd | Admin |

Guía: [docs/onboarding/setup.md](docs/onboarding/setup.md) · fallos: [troubleshooting](docs/onboarding/troubleshooting.md)

## Qué demuestra (y qué no)

| Sí | No |
| --- | --- |
| Ledger como SoT; SQL de audit sin GET `/audit` | Un neobank lanzable |
| Defect lab 7/7 fail-closed | Flags en el demo (`APP_ENV=dev`) |
| Artillery medido y presupuestos **bajados** | SLAs de industria |
| Gate CI: job crítico failed/skipped → rojo | “Pipeline GitHub verde” sin remoto |
| Axe en 4 rutas, 0 violaciones | Certificación WCAG 2.2 AA |

Limitaciones explícitas: [docs/known-limitations.md](docs/known-limitations.md).

## Mapa del repo

| Capa | Rol |
| --- | --- |
| `apps/` | FastAPI + React (SUT) |
| `qa/` | Playwright, Cucumber, Artillery, lab — **no importa** `apps/` |
| `specifications/` | FR/NFR, Gherkin, [RTM](specifications/traceability/rtm.md) |
| `docs/` | ADRs, planes, evidencia |
| `.github/workflows/` + `.gitlab-ci.yml` | PR / main / nightly |

## Quality gates locales

```bash
make lint && make typecheck && make test   # 77 pytest + 10 Vitest (última corrida documentada)
make qa-critical                           # API smoke + E2E Chromium @smoke|@critical
make qa-data                               # ledger + audit_events, sin GET /audit
python3 scripts/ci/require-jobs.py --self-test
```

Suite completa: `qa-smoke`, `qa-regression`, `qa-bdd`, `qa-a11y`, `qa-security`, `qa-zap`, `qa-perf`, `qa-lab-detect`, `qa-pact`, `qa-mutate`, `qa-chaos`.

## Números de la corrida 2026-11-03 (no inventados)

- Pytest **77** passed — [recorte JUnit](docs/evidence/excerpts/junit-pytest-2026-11-03.xml)
- Login p95 **459.5 ms** @ 10 RPS (220 req, 0 errores)
- Lab: **7/7** detectores; mutantes de muestra **KILLED**
- ZAP: **0** High/Critical (6 WARN/info)
- Axe: `violations: []` en login, cuentas, transfer, admin

## Documentación

[Índice](docs/README.md) · [ADRs](docs/architecture/adr/) · [Estrategia QA](docs/qa-strategy/test-strategy.md) · [Performance](docs/performance/) · [CI](docs/ci/quality-gates.md)

## Licencia

Producto ficticio, uso educativo y de portfolio. No conectar a sistemas bancarios reales.
