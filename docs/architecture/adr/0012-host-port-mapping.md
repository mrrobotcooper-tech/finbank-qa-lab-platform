# ADR-0012 — Puertos internos vs puertos publicados

**Estado:** Aceptado  
**Fase:** 1

## Contexto

En la máquina de desarrollo 5432, 6379, 5672, 15672 y 8001 ya estaban ocupados. Si `POSTGRES_PORT` se usa tanto para el bind del host como para la URL del API, cambiarlo rompe la red interna de Compose (`postgres:15432` no existe).

## Decisión

- Puertos **internos** (`POSTGRES_PORT=5432`, `REDIS_PORT=6379`, …) los usa la aplicación dentro de la red Compose.
- Puertos **publicados** (`POSTGRES_HOST_PORT`, `REDIS_HOST_PORT`, `RABBITMQ_HOST_PORT`, `WORKER_HOST_PORT`, …) solo mapean al host.

Valores locales por defecto: 15432, 16379, 25672/25673, 18001, web 5173, API 8000.

## Consecuencias

- El API siempre habla con `postgres:5432` aunque el host use 15432.
- QA desde el host debe usar los `*_HOST_PORT`.
- Documentado en `docs/onboarding/setup.md`.
