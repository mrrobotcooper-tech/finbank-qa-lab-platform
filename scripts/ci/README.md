# Scripts CI compartidos

GitHub Actions y GitLab CI invocan **los mismos** Make targets y este directorio (ADR-0008). No hay una tercera verdad de negocio en YAML.

| Script | Función |
| --- | --- |
| `bootstrap-env.sh` | `.env` desde example + carpetas de reportes |
| `require-jobs.py` | Gate NFR-CI-004: job crítico failed/skipped → rojo |

```bash
python3 scripts/ci/require-jobs.py --self-test
```
