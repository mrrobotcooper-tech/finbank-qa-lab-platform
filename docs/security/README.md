# Seguridad (laboratorio)

Escaneos **solo** contra Compose/localhost (NFR-SEC-010).

| Control | Comando / test |
| --- | --- |
| Headers API + SPA | `qa/automation/security/headers.spec.ts` |
| SUPPORT 403 | `qa/automation/security/authz.spec.ts` |
| Argon2 | SQL `password_hash` + unit `test_password_hash_is_argon2_and_not_plaintext` |
| `.env` | `make qa-secrets` |
| Dependencias | `make qa-deps` |
| ZAP baseline | `make qa-zap` |

Riesgos aceptados del lab HTTP: sin HSTS ni flag `Secure` en cookies (`APP_ENV=dev`). En `prod` el refresh cookie sí lleva `secure=True`. Detalle: [accepted-risks.md](accepted-risks.md).

`make qa-deps`: SUT frontend/backend sin High. El paquete `qa` reporta 1 high en `zod` (devDependency del framework, no del banco).
