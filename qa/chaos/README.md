# Chaos (host)

Los escenarios se ejecutan **en el host** contra Compose, no dentro del contenedor `qa`.

| Script | Inyección | Expectativa |
| --- | --- | --- |
| `redis-down.sh` | `docker compose stop redis` | `GET /ready` → 503, componente redis down |
| `rabbit-down.sh` | `docker compose stop rabbitmq` | POST transferencia 1¢ → `COMPLETED` (FR-NTF-003, outbox SQL) |

Ambos restauran el servicio con `trap`.

```bash
make qa-chaos
```
