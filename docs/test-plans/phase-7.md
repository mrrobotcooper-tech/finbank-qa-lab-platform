# Plan táctico — Fase 7 Accessibility y security

**DoD:** reporte axe real; 403 de SUPPORT; `.env` no commiteado.

## Alcance

| Pieza | Dónde |
| --- | --- |
| Axe WCAG A/AA | `qa/automation/accessibility/critical-routes.spec.ts` |
| Teclado / skip-link | `qa/automation/accessibility/keyboard.spec.ts` |
| Charter WCAG | `qa/automation/exploratory/wcag-critical-flows.md` |
| Authz + headers + cookie | `qa/automation/security/` |
| Hash Argon2 en SQL | `security/password-storage.spec.ts` |
| ZAP baseline local | `make qa-zap` → `qa/reports/zap/` |
| Dependencias | `make qa-deps` |
| Secretos | `make qa-secrets` |

## Cómo correr

```bash
make lint && make typecheck && make test
make qa-a11y
make qa-security
make qa-zap
make qa-deps
make qa-secrets
```

Axe no se documenta como cumplimiento WCAG 2.2 AA total.

## Verificación

- `make lint` / `make typecheck` / `make test`: 65 pytest + 10 Vitest.
- `make qa-a11y`: **6 tests**; reportes `qa/reports/axe/{login,accounts,transfer,admin}.json` con `violations: []`.
- `make qa-security`: **11 tests**, incl. SUPPORT 403 y cookie HttpOnly.
- `make qa-zap`: 0 High/Critical (gate OK). WARN: CSP unsafe-inline, COEP/COOP/CORP, SPA moderna, no-store.
- `make qa-deps`: frontend prod 0; backend pip-audit limpio; `qa` tiene 1 high transitivo en `zod` (no es el SUT).
- `make qa-secrets`: `.env` en `.gitignore`; el árbol local aún no tiene `.git`.
