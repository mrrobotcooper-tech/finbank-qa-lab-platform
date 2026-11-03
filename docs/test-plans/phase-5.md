# Plan táctico — Fase 5 SDD / BDD / TDD

**DoD:** Cucumber corre al menos auth + transfers. RTM sin críticos huérfanos (salvo FR-NTF-003 → Fase 9).

## Alcance

| Pieza | Dónde |
| --- | --- |
| Gherkin ejecutable | `qa/automation/bdd/features/{auth,transfers}.feature` |
| Steps de dominio | `qa/automation/bdd/steps` sobre `framework/` |
| Unitarios de límites | `apps/backend/tests/unit/domain/test_transfers.py` (per-op, daily exactos) |
| JWT expirado | `apps/backend/tests/unit/test_security.py` |
| RTM viva | `specifications/traceability/rtm.md` |

## Cómo correr

```bash
make test            # incluye unitarios nuevos
make qa-bdd          # Cucumber en Docker
```

## Verificación

- `make lint` / `make typecheck` / `make test`: 64 pytest (no integration) + 10 Vitest.
- `make qa-bdd`: **6 escenarios, 25 steps** (`auth.feature` + `transfers.feature`).
