# Riesgos técnicos y decisiones

**Documento:** RSK-001  
**Fase:** 0

## 1. Riesgos

| ID | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-01 | Alcance total (12 módulos + 7 avanzados) diluye calidad | Alto | Fases con DoD; no esqueleto vacío |
| R-02 | Dos runners TS (Playwright + Cucumber) duplican esfuerzo | Medio | Librería `framework/` única; Gherkin solo en aceptación |
| R-03 | Flakiness E2E | Alto | data-testid, auth por API, cero waits fijos |
| R-04 | Tests acoplados a seeds | Alto | Factories + veto `@seed` en regression |
| R-05 | Drift Zod vs Pydantic | Medio | Pact en Fase 9; smoke de schema antes |
| R-06 | Redis caído rompe auth en demo | Medio | Degradación documentada; chaos solo en lab |
| R-07 | Fórmula de saldo mal congelada | Alto | ADR-0002 + test de reconciliación como quality gate |
| R-08 | Defect flags en perfil no test | Crítico | Fail-closed ADR-0007; test que lo demuestra |
| R-09 | CI demasiado lenta | Medio | Tags; nightly para lo caro |
| R-10 | Mutation score malinterpretado | Bajo | Documentar limitaciones en Fase 9 |
| R-11 | ZAP o Artillery usados contra hosts ajenos | Crítico | Base URL allowlist localhost/compose |
| R-12 | Secretos en git | Alto | `.env.example` + gitignore; scan en CI |
| R-13 | Playwright WebKit en CI Linux | Medio | WebKit en nightly; PR en Chromium |
| R-14 | Concurrencia de transferencias mal testeada | Alto | Unique + SELECT FOR UPDATE; test de carrera en Fase 6 |
| R-15 | Outbox nunca se drena | Medio | Métrica lag + data test |

## 2. Decisiones ya tomadas (resumen)

Detalle en [adr/](architecture/adr/).

1. Monolito modular, no microservicios.
2. Ledger verdad, saldo proyección.
3. JWT + refresh Redis.
4. Enteros para dinero; sin FX.
5. Auditoría sin GET completo.
6. QA independiente.
7. Defect lab fail-closed.
8. GitHub primario, GitLab espejo.
9. Cucumber + Playwright Test.
10. Outbox + `finbank-mocks`.

## 3. Decisiones aplazadas (no bloquean Fase 1)

| Tema | Se decide en |
| --- | --- |
| Librería exacta de rate limit (slowapi vs Redis propio) | Fase 2 |
| playwright-bdd vs Cucumber puro (ADR-0009 ya elige Cucumber puro; se revisa si DX duele) | Fase 5 |
| WireMock adicional vs solo `finbank-mocks` | Fase 9 |
| OpenTelemetry además de logs/métricas | Fase 8 |
| Cookie vs header para access token (ADR-0003: access en memoria, refresh cookie) | Solo se reabre con hallazgo de seguridad |

## 4. Amenazas a la honestidad del laboratorio

- README que afirma módulos no ejecutables.
- Tests que asertan status 200 y nada más.
- Reportes Allure commiteados de una corrida ajena.
- Cobertura 90 % con reglas de dinero sin test.

Cualquiera de esas cuatro se trata como defecto P0 de proceso.
