# Plan táctico — Fase 9 Advanced

**DoD:** matriz de detección con al menos un defecto ON que rompe un test concreto.

## Alcance

| Pieza | Dónde |
| --- | --- |
| Defect lab | `qa/defect-lab/` + `make qa-lab-detect` |
| Pact muestra | `qa/automation/contract/` + `make qa-pact` |
| Mutation muestra | `qa/mutations/` + `make qa-mutate` |
| Chaos Redis/Rabbit | `qa/chaos/` + `make qa-chaos` (host) |
| Charters | `qa/automation/exploratory/` |
| TDM | `docs/data-quality/tdm.md` |

## Defectos

Siete categorías: FUN, AUT, DAT, VAL, SEC, REL, AUD. Fail-closed si `APP_ENV` ∉ {test, ci}.

## Cómo correr

```bash
make lint && make typecheck && make test
make qa-lab-detect
make qa-pact
make qa-mutate
make qa-chaos
```

## Verificación (2026-11-03)

- `make lint` / `typecheck` / `test`: ruff+mypy OK; **77** pytest; **10** Vitest; QA tsc/eslint OK.
- `make qa-lab-detect`: 7 detectores OFF pass; 7 ON rompen el test nombrado.
- `make qa-pact`: `GET /health` `status=ok service=finbank env=dev`.
- `make qa-mutate`: mutante `require_positive_amount` KILLED; mutante `toCents` KILLED.
- `make qa-chaos`: Redis → `/ready` 503; Rabbit → transfer `COMPLETED`; stack `ready=ok` al restaurar.
