# Defect Injection Lab

Catálogo: [catalog.md](catalog.md). Matriz: [matrix.md](matrix.md). ADR: `docs/architecture/adr/0007-defect-injection-isolation.md`.

```bash
make qa-lab-detect
```

El script corre los detectores con lab OFF (deben pasar) y después cada ID con `APP_ENV=test FINBANK_DEFECTS=<id>` (el detector debe fallar).
