# Checklist de revisión — Fase 0

**Aprobado el 2026-11-03.** Fase 1 ejecutada a continuación.

## Entregables

- [x] Visión del producto
- [x] Alcance in / out / pospuesto
- [x] Requisitos funcionales y no funcionales con ID
- [x] Arquitectura de sistema y procesos
- [x] Diagrama de componentes
- [x] Diagramas de interacción (transfer, pago, login)
- [x] Modelo de datos y reglas SQL previstas
- [x] Arquitectura del framework QA
- [x] Estrategia de testing
- [x] RTM propuesta (sin IDs de test inventados)
- [x] Estructura de repositorio
- [x] Roadmap Fase 0–11
- [x] Riesgos y ADRs

## Preguntas para el revisor

1. ¿Se acepta el **monolito modular** o se exige microservicios por dominio?
2. ¿Se acepta **no** exponer el audit log completo por API?
3. ¿Se aceptan **dos runners** TypeScript (Playwright Test + Cucumber)?
4. ¿Monedas solo `ARS` y `USD` sin FX?
5. ¿GitHub como CI de referencia y GitLab como espejo es suficiente?
6. ¿Algún recorte de alcance (pagos programados, WebKit en PR, Grafana) debe moverse?

## Criterios para aprobar

- El SUT es suficientemente rico para un laboratorio de QA.
- El framework QA queda independiente.
- Hay al menos un requisito crítico verificable solo con SQL.
- Las fases son incrementales y verificables.
- No se pide código de aplicación en esta fase.

## Respuesta esperada para continuar

Una de:

- `APROBADO — iniciar Fase 1`
- `APROBADO CON CAMBIOS — [lista]`
- `RECHAZADO — [motivos]`
