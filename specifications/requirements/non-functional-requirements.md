# Requisitos no funcionales — FinBank

**Documento:** REQ-NFR-001  
**Fase:** 8  
**Estado:** Presupuestos PERF recalibrados

Los umbrales de performance son **presupuestos de proyecto**, no estándares de la industria. Recalibrados en Fase 8: ver `docs/performance/budgets.md`.

## Seguridad

| ID | Requisito |
| --- | --- |
| NFR-SEC-001 | Contraseñas se almacenan con hash adaptativo (Argon2). Nunca en claro. |
| NFR-SEC-002 | Secretos viven en variables de entorno; el repo solo tiene `.env.example`. |
| NFR-SEC-003 | API exige autenticación excepto en endpoints públicos explícitos (health, registro, login, recovery). |
| NFR-SEC-004 | Autorización por rol en cada operación de dinero o administración. |
| NFR-SEC-005 | Tokens de acceso de vida corta; refresh rotativo y revocable en Redis. |
| NFR-SEC-006 | Rate limiting en login y operaciones sensibles. |
| NFR-SEC-007 | Headers de seguridad en API y frontend servido. |
| NFR-SEC-008 | Entrada validada con Pydantic/Zod; consultas parametrizadas (SQLAlchemy). |
| NFR-SEC-009 | Escaneo de dependencias en CI. |
| NFR-SEC-010 | ZAP, si se usa, solo contra localhost/compose. |

## Accesibilidad

| ID | Requisito |
| --- | --- |
| NFR-A11Y-001 | Flujos críticos (login, cuentas, transferencia, admin) se analizan con axe-core. |
| NFR-A11Y-002 | Formularios tienen labels, nombres accesibles y mensajes de error asociados. |
| NFR-A11Y-003 | Navegación por teclado y foco visible en diálogos. |
| NFR-A11Y-004 | La suceso de axe no se documenta como cumplimiento WCAG 2.2 AA total. |

## Performance (presupuestos vigentes, Fase 8)

Medidos en Docker local el 2026-11-03. Detalle: `docs/performance/`.

| ID | Presupuesto vigente | Base de medición |
| --- | --- | --- |
| NFR-PERF-001 | Login p95 < 600 ms a 10 RPS sostenidos | p95 459.5 ms @ 10 RPS (220 req) |
| NFR-PERF-002 | Consulta de cuentas p95 < 100 ms a 20 RPS | p95 13.1 ms @ 20 RPS (440 req) |
| NFR-PERF-003 | Transferencia p95 < 100 ms a 3 RPS (misma cuenta origen) | p95 22.9 ms @ 3 RPS (68 POST 1 ¢) |
| NFR-PERF-004 | Error rate < 1 % en load nominal | 0 % en la corrida |
| NFR-PERF-005 | Soak y stress no bloquean PRs | Política CI |

## Observabilidad

| ID | Requisito |
| --- | --- |
| NFR-OBS-001 | Logs estructurados JSON con `correlation_id`, `user_id` opcional, `event`. |
| NFR-OBS-002 | El backend acepta o genera `X-Correlation-ID` y lo propaga a logs, auditoría y mensajes. |
| NFR-OBS-003 | Endpoint `/metrics` compatible con Prometheus. |
| NFR-OBS-004 | Dashboards Grafana locales para API, worker y colas. |
| NFR-OBS-005 | Health checks liveness/readiness por servicio. |

## Fiabilidad y datos

| ID | Requisito |
| --- | --- |
| NFR-REL-001 | Transferencia COMPLETED es atómica respecto al ledger (una transacción SQL). |
| NFR-REL-002 | Publicación a RabbitMQ usa outbox o equivalente para no perder el evento de negocio. |
| NFR-REL-003 | Timeouts explícitos a Redis, RabbitMQ y pasarela mock. |
| NFR-DAT-001 | Importes en unidades menores enteras; nunca `float`. |
| NFR-DAT-002 | Constraints de integridad en PostgreSQL (PK, FK, unique, check). |
| NFR-DAT-003 | Seeds y factories producen datos ficticios reproducibles. |

## Operación y calidad de proceso

| ID | Requisito |
| --- | --- |
| NFR-CI-001 | PR ejecuta lint, typecheck, unit y smoke API. |
| NFR-CI-002 | `main` ejecuta regresión ampliada. |
| NFR-CI-003 | Nightly ejecuta a11y, data, security checks y performance smoke. |
| NFR-CI-004 | Un fallo crítico no puede publicarse como pipeline exitoso. |
| NFR-ISO-001 | Los tests no comparten estado mutable. |
| NFR-ISO-002 | Defect Injection Lab desactivado por defecto. |
