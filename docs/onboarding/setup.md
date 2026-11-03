# Setup local

FinBank se levanta con Docker Compose. No hay ambiente productivo.

## Requisitos

- Docker y Docker Compose
- Python 3.12+ (solo para tests/lint del backend fuera de Compose)
- Node 22+ (solo para tests/lint del frontend fuera de Compose)

## Arranque

```bash
git clone https://github.com/mrrobotcooper-tech/finbank-qa-lab-platform.git
cd finbank-qa-lab-platform
cp .env.example .env   # si aún no existe
make up
make ps
make ready
```

Cuando todos los servicios están `healthy`:

| Servicio | URL |
| --- | --- |
| Web | http://localhost:5173 |
| API health | http://localhost:8000/health |
| API ready | http://localhost:8000/ready |
| API docs | http://localhost:8000/docs |
| Mocks health | http://localhost:8090/health |
| Worker health | http://localhost:18001/health |
| PostgreSQL (host) | localhost:15432 |
| Redis (host) | localhost:16379 |
| RabbitMQ AMQP (host) | localhost:25672 |
| RabbitMQ management | http://localhost:25673 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Los puertos publicados en el host están separados de los puertos internos de Compose (`POSTGRES_HOST_PORT` vs `POSTGRES_PORT`, etc.) para no chocar con servicios locales.

Grafana: usuario `admin`, password la de `GRAFANA_ADMIN_PASSWORD` en `.env`.

## Tests

```bash
# backend (sin Compose)
cd apps/backend && python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -m "not integration"
ruff check src tests
mypy

# frontend
cd apps/frontend && npm install
npm test
npm run typecheck
npm run lint

# integración contra el stack levantado
make test-integration
```

## Parar

```bash
make down
```

Datos de Postgres/Redis/Rabbit quedan en volúmenes. Para resetear: `docker compose down -v`.

## Usuarios demo (Fase 2)

| Correo | Clave | Rol |
| --- | --- | --- |
| ana@finbank.test | Customer1! | Cliente con saldo ARS/USD |
| bruno@finbank.test | Customer1! | Cliente (una cuenta bloqueada) |
| cara@finbank.test | Customer1! | Cliente sin saldo |
| support@finbank.test | SupportPassw0rd | Soporte (solo lectura) |
| admin@finbank.test | AdminPassw0rd | Admin |

Cuenta destino de demo: CBU ficticio de Bruno `32200000000000000003`. El mock de pagos rechaza el destinatario `REJECT`.

## QA smoke, BDD, datos y seguridad (Fases 3–7)

Con el stack healthy:

```bash
make qa-smoke
```

```bash
make qa-regression
```

Corre Playwright (API + Chromium) en Docker contra `web` y `api`. No importa código de `apps/`. Firefox/WebKit: `QA_BROWSERS=full` (Fase 10).

```bash
make qa-bdd
make qa-data
```

Cucumber (auth + transfers) y aserciones SQL de ledger/auditoría. El rol `finbank_qa_reader` es de solo lectura.

```bash
make qa-a11y
make qa-security
make qa-zap
make qa-secrets
```

Axe en login/cuentas/transfer/admin, 403 de SUPPORT, ZAP solo contra Compose, `.env` fuera de git.

## Performance, lab y chaos (Fases 8–9)

```bash
make qa-perf
make qa-lab-detect
make qa-pact
make qa-mutate
make qa-chaos
```

Artillery y chaos corren **en el host** (no en el contenedor `qa`). Informe: `docs/performance/`. TDM: `docs/data-quality/tdm.md`.

## CI/CD (Fase 10)

GitHub Actions (referencia) y GitLab CI (espejo). Documentación: [docs/ci/quality-gates.md](../ci/quality-gates.md).

```bash
python3 scripts/ci/require-jobs.py --self-test
make qa-critical
```

Firefox/WebKit: `QA_BROWSERS=full make qa-smoke` (nightly).

## Recorrido, FAQ y evidencia (Fase 11)

- [Recorrido del laboratorio](demo.md)
- [FAQ del laboratorio](lab-faq.md)
- [Troubleshooting](troubleshooting.md)
- [Evidencia](../evidence/2026-11-03.md)
- [Limitaciones](../known-limitations.md)
