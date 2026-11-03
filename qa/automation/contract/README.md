# Contratos (muestra Pact)

Consumer: `finbank-qa`. Provider: `finbank-api`.

Interacción de muestra: `GET /health` → `{status, service, environment, correlation_id}`.

```bash
make qa-pact
```

El verificador pega al API live y compara contra `pacts/finbank-qa-finbank-api.json`. No es un broker Pact; es un contrato versionado en el repo.
