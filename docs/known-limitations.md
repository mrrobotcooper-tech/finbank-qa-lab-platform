# Limitaciones conocidas (cierre Fase 11)

Afirmar esto en una entrevista es más útil que ocultarlo.

| Tema | Estado |
| --- | --- |
| Remoto git / CI ejecutada | Código en [finbank-qa-lab-platform](https://github.com/mrrobotcooper-tech/finbank-qa-lab-platform). El primer verde de Actions es el de ese remoto, no una captura previa. |
| Soak 24 h / stress | NFR-PERF-005: no bloquea PR. No corrido. |
| Login 20 RPS / cuentas 50 RPS / transfer 10 RPS | No sostenidos o no medidos. Ver presupuestos recalibrados. |
| Firefox / WebKit | Cableado (`QA_BROWSERS=full`). Verificación de Fase 10 en esta máquina: Chromium. |
| WCAG 2.2 AA | Axe en 4 rutas + charter. No es certificación. |
| Mutation | Dos mutantes de muestra, ambos KILLED. Sin score %. |
| `qa` npm audit | 1 high transitivo en `zod`. El SUT frontend prod y pip-audit backend: limpios en Fase 7. |
| Lab HTTP | Sin HSTS ni cookie `Secure` (`APP_ENV=dev`). |
| FR-TRF-001 E2E entre propias ARS | El registro no abre segunda cuenta ARS. Cubierto en dominio. |
| Reversa / FX / créditos | Fuera de v1. |
