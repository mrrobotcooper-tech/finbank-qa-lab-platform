# FinBank API

Backend FastAPI del System Under Test. Fase 2: autenticación, cuentas, ledger, transferencias, pagos mock, admin y auditoría append-only.

```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
mypy
```

Arranque local (infraestructura vía Compose):

```bash
alembic upgrade head
python -m finbank.seed
uvicorn finbank.main:app --reload --host 0.0.0.0 --port 8000
```
