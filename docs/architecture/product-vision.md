# Visión del producto — FinBank

**Documento:** VIS-001  
**Fase:** 0  
**Estado:** En revisión  
**Audiencia:** arquitectura, QA, ingeniería, evaluadores técnicos

## 1. Declaración de visión

FinBank es una plataforma bancaria digital ficticia que funciona como **System Under Test** de un ecosistema de Quality Engineering de nivel Senior.

El producto simula la operación core de un banco retail digital: identidad, cuentas, transferencias, pagos, administración, notificaciones y auditoría. El ecosistema QA no es un conjunto de scripts colgados al final: es una plataforma paralela, independiente del código de aplicación, capaz de diseñar estrategia, automatizar, investigar defectos, validar datos sin depender de APIs, medir performance, evaluar seguridad y accesibilidad, y gobernar calidad en CI/CD.

FinBank debe poder presentarse en GitHub y en entrevistas técnicas como evidencia de que un Senior QA Automation Engineer puede:

1. Construir un SUT realista, no un CRUD de demostración.
2. Diseñar una estrategia de testing, no solamente automatizar casos existentes.
3. Verificar reglas de negocio en UI, API, base de datos, eventos y auditoría.
4. Detectar defectos reales, incluidos defectos intencionales del Defect Injection Lab.
5. Producir reportes, métricas y quality gates verificables.

## 2. Problema que resuelve

Los portfolios de QA suelen pecar de uno de estos extremos:

- Colecciones de tests Playwright contra un sitio público ajeno, sin control del SUT.
- Demos frontend sin reglas financieras, sin ledger, sin auditoría y sin datos.
- Documentación de estrategia sin implementación ejecutable.

FinBank evita esos tres fallos. El SUT es propio, controlable y defectuoso a propósito en laboratorio. El framework QA es profesional. La evidencia es reproducible.

## 3. Usuarios del sistema

### 3.1 Usuarios de negocio (ficticios, dentro de FinBank)

| Rol | Intención |
| --- | --- |
| `CUSTOMER` | Operar cuentas propias, transferir, pagar, consultar historial. |
| `SUPPORT` | Consultar usuarios y operaciones; no mueve dinero ni cambia roles. |
| `ADMIN` | Bloquear cuentas, gestionar roles, ver indicadores y auditoría operativa. |

### 3.2 Usuarios del ecosistema (reales, fuera de FinBank)

| Perfil | Intención |
| --- | --- |
| Ingeniero QA / SDET | Ejecutar, extender y demostrar el framework. |
| Entrevistador técnico | Evaluar profundidad, no solo cobertura de UI. |
| El autor del portfolio | Explicar decisiones, trade-offs y evidencia. |

## 4. Principios de producto

1. **Ficticio y aislado.** Cero dinero real, cero PII real, cero integraciones productivas.
2. **Controlable.** Cada dependencia externa es mockeable. Los defectos se activan solo en laboratorio.
3. **Observable.** Correlation IDs, logs estructurados, métricas, auditoría append-only.
4. **Verificable sin API.** Las reglas críticas tienen evidencia en PostgreSQL aunque no exista endpoint.
5. **Separación estricta.** Aplicación, automatización, datos de test, especificaciones e infraestructura no se mezclan.
6. **Calidad demostrable por ejecución.** Un documento no sustituye un test que corre.

## 5. Propuesta de valor QA

El valor de FinBank no es “tener un login”. Es poder responder, con evidencia:

- ¿Qué requisito cubre este test?
- ¿Qué ocurre en el ledger cuando la API responde 201?
- ¿Qué pasa si Redis cae a mitad de una transferencia?
- ¿El framework detecta un defecto de autorización inyectado?
- ¿Una mutación en la regla de límite diario sobrevive a la suite?
- ¿Un pipeline verde puede ocultar un fallo crítico? (no)

## 6. Criterios de éxito del producto (visión)

La visión se considera cumplida cuando, al cierre de la Fase 11:

- Un evaluador puede clonar, levantar el entorno y ejecutar al menos smoke, API, un flujo E2E y una validación SQL de reconciliación.
- Existe RTM para requisitos críticos, con tests y justificación de huecos.
- El Defect Injection Lab tiene catálogo, activación controlada y tests que fallan cuando el defecto está activo.
- Hay reportes Allure/JUnit, no capturas inventadas.
- La documentación explica *por qué*, no solo *qué*.

## 7. Fuera de la visión

FinBank no pretende ser un core banking de producción, un neobank lanzable, ni una plataforma multi-país con FX, créditos, inversiones o cumplimiento regulatorio real (BCRA, PCI-DSS productivo, SOC2). Es un SUT de ingeniería de calidad con fidelidad suficiente para que las pruebas importen.
