# Mutation sample

Muestra acotada, no un score de portfolio inventado.

| Motor | Superficie | Cómo |
| --- | --- | --- |
| mutmut (si está instalado) | `apps/backend/src/finbank/domain/money.py` | `mutmut run` |
| muestra Python | un mutante en `require_positive_amount` | `python qa/mutations/python_sample.py` |
| Stryker-style JS | un mutante en `toCents` | `node qa/mutations/js_sample.mjs` |

```bash
make qa-mutate
```

El Make exige que ambos mutantes de muestra mueran. mutmut extra es informativo.
