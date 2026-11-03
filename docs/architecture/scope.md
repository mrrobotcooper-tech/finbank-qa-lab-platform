# Alcance — FinBank QA Platform

**Documento:** SCO-001  
**Fase:** 0  
**Estado:** En revisión

Este documento delimita qué entra en el producto, qué queda fuera, y qué se pospone con justificación. El detalle normativo vive en [specifications/requirements/](../../specifications/requirements/).

## 1. Alcance funcional (in)

### 1.1 Autenticación y usuarios

- Registro, login, logout.
- Recuperación de contraseña **simulada** (token + evento de notificación).
- Validación de credenciales, bloqueo temporal por intentos fallidos.
- Sesiones con revocación y expiración.
- Roles `CUSTOMER`, `SUPPORT`, `ADMIN` y matriz de permisos.
- Perfil, actualización de datos personales, historial de actividad.

### 1.2 Cuentas

- Alta de cuentas (CHECKING / SAVINGS) en ARS o USD.
- Consulta de cuentas, saldo disponible, saldo retenido, estado, límites.
- Historial de movimientos (ledger).
- Bloqueo / desbloqueo (admin) y cierre lógico.

### 1.3 Transferencias

- Entre cuentas propias y entre clientes.
- Validación de titularidad, saldo, moneda, límites diarios y por operación.
- Idempotencia (`Idempotency-Key`).
- Estados: `PENDING`, `COMPLETED`, `REJECTED`, `FAILED`.
- Identificador único de operación y auditoría.

### 1.4 Pagos ficticios

- Servicios, tarjetas, facturas.
- Pagos programados, pendientes y rechazados.
- Historial.
- Pasarela externa **mockeada** (nunca un adquirente real).

### 1.5 Administración

- Panel admin: usuarios, bloqueo de cuentas, consulta de operaciones.
- Indicadores operativos agregados.
- Gestión de roles.
- Auditoría operativa **limitada** (no el log append-only completo).

### 1.6 Notificaciones

- Canales simulados: email, SMS, in-app.
- Publicación asíncrona por RabbitMQ.
- Persistencia del ciclo de vida del mensaje (`QUEUED`, `SENT`, `FAILED`).

### 1.7 Auditoría

- Registro append-only: actor, operación, entidad, before/after, correlation ID, timestamp.
- **Sin endpoint de listado completo** a propósito: es el caso canónico de Data Testing sin API.

## 2. Alcance no funcional (in)

| ID | Área | Compromiso de diseño |
| --- | --- | --- |
| NFR-SEC | Seguridad | AuthN/AuthZ en UI y API, hashing de secretos, headers, rate limit, secretos fuera del repo |
| NFR-A11Y | Accesibilidad | WCAG 2.2 AA como referencia; axe-core no se trata como cumplimiento total |
| NFR-PERF | Performance | Presupuestos de proyecto medidos, no SLAs universales inventados |
| NFR-OBS | Observabilidad | Logs JSON, correlation ID, `/metrics`, Grafana local |
| NFR-REL | Resiliencia | Timeouts, reintentos acotados, degradación documentada, chaos en laboratorio |
| NFR-ISO | Aislamiento | Tests independientes, datos únicos, defectos solo en lab |
| NFR-REP | Reproducibilidad | Docker Compose, seeds sintéticos, CI determinista en lo posible |

## 3. Fuera de alcance (out)

Estas exclusiones son deliberadas. Incluirlas diluiría profundidad y fingiría un core banking que este proyecto no es.

- Dinero real, CBU/CVU reales, KYC/AML regulatorios, scoring crediticio.
- Integraciones con bancos, tarjetas o bureaus reales.
- FX / conversión de moneda (un transfer multi-currency se **rechaza**).
- Créditos, inversiones, plazos fijos, cheques, efectivo.
- App nativa iOS/Android.
- Kubernetes, service mesh, multi-región.
- GraphQL, gRPC público, event sourcing completo tipo EventStore.
- Open banking (PSD2) y biometría.
- Datos personales reales, scraping, o pruebas contra sistemas ajenos.

## 4. Alcance del ecosistema QA (in)

Los 12 módulos principales y las 7 especializaciones avanzadas del prompt maestro están **dentro de alcance**, con esta precisión:

- Cada módulo debe tener implementación **ejecutable** o, si depende de una fase posterior, declaración explícita de pendiente.
- Exploratory testing es proceso documentado, no automatización forzada.
- Mutation, chaos y soak **no** corren en cada PR.
- OWASP ZAP solo contra el entorno local aislado.

## 5. Recortes conscientes de v1 (pospuestos, no negados)

| Tema | Motivo | Reevaluación |
| --- | --- | --- |
| Reversa de transferencias | Complejidad de compensación; primero el camino feliz y rechazo | Fase 2 tardía si el ledger está sólido |
| Multi-tenant / sucursales | No aporta al relato QA | Fuera |
| FX | Introduce dominio entero | Fuera de v1 |
| Kubernetes manifests | Compose cubre reproducibilidad local/CI | Fase 11 opcional |
| OpenTelemetry traces distribuidas | Correlation ID + logs + métricas alcanzan el relato; traces son valor añadido | Fase 8–10 si hay margen |

## 6. Definición de MVP por fase

El MVP de **producto bancario** se alcanza al cierre de la Fase 2: un cliente puede registrarse, ver una cuenta seed, transferir y pagar contra mocks, y un admin puede bloquear.

El MVP de **plataforma QA** se alcanza al cierre de la Fase 4: hay framework, E2E, API y smoke en local/Docker.

La visión de documentación de portfolio se cubre en Fase 11 (`docs/onboarding/`, `docs/evidence/`). Kubernetes sigue fuera de v1.
