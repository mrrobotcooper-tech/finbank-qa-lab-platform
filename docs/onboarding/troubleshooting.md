# Troubleshooting

## Compose no queda healthy

```bash
make ps
make logs
docker compose logs api --tail 80
```

API espera Postgres + Redis + Rabbit + mocks. El `start_period` del healthcheck es ~45 s. Si `alembic upgrade` o el seed fallan, el contenedor no pasa a healthy.

Reset de datos: `docker compose down -v` (borra volúmenes).

## Puerto ocupado

Los puertos del **host** no son los internos (ADR-0012). En `.env`: `API_HOST_PORT`, `WEB_HOST_PORT`, `POSTGRES_HOST_PORT` (15432), Redis 16379, Rabbit 25672/25673.

## `make qa-data` o BDD: permission denied / relation

Falta el GRANT al lector:

```bash
make qa-grant
```

Password del reader: `QA_READER_PASSWORD` en `.env` (default de example: `change_me_qa`). Host desde el contenedor `qa`: `postgres:5432`. Desde el host: `127.0.0.1:15432`.

## Playwright no llega a `web`

En Docker, `QA_BASE_URL=http://web` y `QA_API_URL=http://api:8000`. En el host: `http://localhost:5173` y `http://localhost:8000`. No mezclar.

## Artillery contra el contenedor `qa`

No. `make qa-perf` corre **en el host** hacia `http://127.0.0.1:8000`. Dentro de `qa` ese localhost no es la API.

## Redis/Rabbit “siguen caídos” después de chaos

Los scripts tienen `trap` de restore. Si se mató el script a mitad:

```bash
docker compose start redis rabbitmq
make ready
```

## Defectos que “no se activan”

`APP_ENV` tiene que ser `test` o `ci`. El demo usa `dev`: `FINBANK_DEFECTS` y `X-Finbank-Defects` son no-op (log de error). Eso es ADR-0007, no un bug.

## Login 423 / Ana sin saldo

Lockout: 5 intentos. Esperar `LOGIN_LOCKOUT_SECONDS` o recrear volúmenes.  
Ana se usa para fondear y para Artillery (1 ¢). No afirmar su saldo residual en tests `@seed`.

## `ruff` / `pytest` not found

```bash
cd apps/backend && source .venv/bin/activate
# o
export PATH="$PWD/apps/backend/.venv/bin:$PATH"
```

## Quality gate en local

```bash
python3 scripts/ci/require-jobs.py --self-test
```

`NEEDS_JSON` vacío → exit 2. Un job `skipped`/`failure` → exit 1.

## ZAP exit 2 con reporte OK

El wrapper `zap-gate.mjs` solo falla en High/Critical. El binario de ZAP puede salir ≠ 0 por WARN; el Makefile usa `-` y después el gate.
