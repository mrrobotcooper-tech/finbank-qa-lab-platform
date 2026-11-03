# Evidencia

Regla: no se commitean dumps Allure/ZAP/axe. Sí se versiona un **recorte** con fecha y comando.

- [Corrida 2026-11-03](2026-11-03.md)
- Artefactos locales (gitignored): `qa/reports/`
- Performance: [docs/performance/](../performance/)
- Quality gates: [docs/ci/quality-gates.md](../ci/quality-gates.md)

Generar Allure HTML en local (opcional, no forma parte del DoD commiteado):

```bash
npx --prefix qa --yes allure generate qa/reports/allure-results -o qa/reports/allure --clean
```
