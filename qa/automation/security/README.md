# Security checks

Authz, headers, cookie de refresh, almacenamiento Argon2 y ausencia de GET `/audit`.

ZAP baseline (solo compose/localhost): `make qa-zap`.
Auditoría de dependencias: `make qa-deps`.
`.env` no versionado: `make qa-secrets`.
