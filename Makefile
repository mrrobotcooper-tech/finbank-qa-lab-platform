.PHONY: help env up down logs ps ready lint typecheck test test-integration qa-smoke qa-regression qa-grant qa-bdd qa-data qa-a11y qa-security qa-zap qa-deps qa-secrets qa-perf qa-lab-detect qa-pact qa-mutate qa-chaos qa-critical build

COMPOSE := docker compose

help:
	@echo "FinBank Phase 11"
	@echo "  make env               Create .env from .env.example if missing"
	@echo "  make up                Build and start the stack"
	@echo "  make down              Stop the stack"
	@echo "  make logs              Follow API, worker, mocks and web logs"
	@echo "  make ps                Show compose status"
	@echo "  make ready             Curl /health and /ready"
	@echo "  make lint              Ruff + ESLint (apps + qa)"
	@echo "  make typecheck         mypy + tsc (apps + qa)"
	@echo "  make test              Backend pytest + frontend vitest"
	@echo "  make test-integration  Live /ready and banking against compose"
	@echo "  make qa-smoke          Playwright @smoke in Docker against the SUT"
	@echo "  make qa-regression     Playwright functional + data + a11y/security críticos"
	@echo "  make qa-bdd            Cucumber auth+transfers en Docker"
	@echo "  make qa-data           Playwright proyecto data (SQL) en Docker"
	@echo "  make qa-a11y           axe-core + teclado en rutas críticas"
	@echo "  make qa-security       headers, authz SUPPORT 403, Argon2"
	@echo "  make qa-zap            ZAP baseline solo contra Compose"
	@echo "  make qa-deps           npm audit + pip-audit (reportes)"
	@echo "  make qa-secrets        Falla si .env está versionado"
	@echo "  make qa-perf           Artillery login/cuentas/transfers (host)"
	@echo "  make qa-lab-detect     Defect lab OFF pass / ON fail"
	@echo "  make qa-pact           Contrato GET /health contra API live"
	@echo "  make qa-mutate         Muestra mutación Python + JS"
	@echo "  make qa-chaos          Redis 503 + Rabbit transfer COMPLETED"
	@echo "  make qa-critical       API smoke + E2E Chromium @smoke|@critical (gate PR)"
	@echo "  make build             Compose build only"

env:
	@test -f .env || cp .env.example .env

up: env
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api worker mocks web

ps:
	$(COMPOSE) ps

ready:
	@curl -sf http://127.0.0.1:8000/health | python3 -m json.tool
	@curl -sf http://127.0.0.1:8000/ready | python3 -m json.tool
	@curl -sf http://127.0.0.1:18001/health | python3 -m json.tool

lint:
	cd apps/backend && ruff check src tests
	cd apps/frontend && npm run lint
	cd qa && npm run lint

typecheck:
	cd apps/backend && mypy
	cd apps/frontend && npm run typecheck
	cd qa && npm run typecheck

test:
	mkdir -p qa/reports qa/reports/allure-results
	cd apps/backend && pytest -m "not integration" --junitxml=../../qa/reports/junit-pytest.xml --alluredir=../../qa/reports/allure-results
	cd apps/frontend && npm run test

test-integration:
	cd apps/backend && FINBANK_INTEGRATION=1 FINBANK_API_URL=http://127.0.0.1:8000 pytest -m integration

qa-grant: env
	$(COMPOSE) up -d postgres
	$(COMPOSE) exec -T postgres sh -c 'until pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"; do sleep 1; done; psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "GRANT USAGE ON SCHEMA public TO finbank_qa_reader; GRANT SELECT ON ALL TABLES IN SCHEMA public TO finbank_qa_reader; GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO finbank_qa_reader;"'

qa-smoke: env
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa

qa-critical: env qa-grant
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa npx playwright test --project=api --project=e2e-chromium --grep "@smoke|@critical"

qa-regression: env qa-grant
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa npx playwright test --grep "@smoke|@regression|@critical"

qa-bdd: env qa-grant
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa npm run test:bdd

qa-data: env qa-grant
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa npx playwright test --project data

qa-a11y: env
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa npx playwright test --project a11y

qa-security: env qa-grant
	$(COMPOSE) up -d --build web api
	$(COMPOSE) --profile qa run --rm --build qa npx playwright test --project security

qa-zap: env
	mkdir -p qa/reports/zap
	$(COMPOSE) up -d --build web api
	-$(COMPOSE) --profile zap run --rm --user 0 zap
	node qa/scripts/zap-gate.mjs qa/reports/zap/zap-baseline.json

qa-deps:
	mkdir -p qa/reports/deps
	cd apps/frontend && npm audit --omit=dev --json > ../../qa/reports/deps/frontend-npm-audit.json || true
	cd qa && npm audit --json > reports/deps/qa-npm-audit.json || true
	cd apps/backend && .venv/bin/python -m pip install -q pip-audit && .venv/bin/pip-audit -f json -o ../../qa/reports/deps/backend-pip-audit.json || true
	@echo "Reportes en qa/reports/deps/"

qa-secrets:
	@grep -qx '.env' .gitignore
	@test -f .env.example
	@if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
	  if git ls-files --error-unmatch .env >/dev/null 2>&1; then echo ".env está versionado"; exit 1; fi; \
	  echo ".env no está en el índice de git"; \
	else \
	  echo "sin repositorio git; .gitignore cubre .env"; \
	fi

qa-perf: env
	$(COMPOSE) up -d api
	mkdir -p qa/reports/perf
	cd qa && npm run test:perf

qa-lab-detect:
	bash qa/scripts/lab-detect.sh

qa-pact: env
	$(COMPOSE) up -d api
	cd qa && npm run test:pact

qa-mutate:
	python3 qa/mutations/python_sample.py
	node qa/mutations/js_sample.mjs

qa-chaos: env
	$(COMPOSE) up -d api redis rabbitmq
	bash qa/chaos/redis-down.sh
	bash qa/chaos/rabbit-down.sh
	$(COMPOSE) up -d redis rabbitmq
	@echo "Chaos restaurado; comprobá make ready si el API tardó en reconectar."

build:
	$(COMPOSE) build
