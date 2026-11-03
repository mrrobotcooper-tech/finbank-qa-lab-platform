# Charter exploratorio — WCAG 2.2 AA (flujos críticos)

**Tipo:** sesión manual. Axe es red, no cierre (NFR-A11Y-004).
**Duración sugerida:** 45–60 min.
**Ambiente:** `make up`, Chromium + teclado, zoom 200 %, lector si está disponible.

## Misión

Encontrar barreras en login, cuentas, transferencia y administración que axe no ve: foco perdido, orden de tab incoherente, errores no anunciados, contraste en estados hover/disabled, y nombres accesibles de controles dinámicos.

## Oráculos

- Todo control operable tiene nombre accesible.
- El orden de tab sigue el orden visual.
- El foco es visible sobre header oscuro y sobre formularios claros.
- `role="alert"` anuncia errores de login/transferencia.
- No hay trampa de teclado.
- Zoom 200 % no tapa el submit.

## Sesión (guion mínimo)

1. Login: skip-link, tab por correo/clave/submit, error 401 anunciado, ingreso de Ana.
2. Cuentas: tabla leíble, enlace de CBU alcanzable, volver con teclado.
3. Transferencia: origen, CBU, importe, submit; probar destino inválido y leer el alert.
4. Admin (admin@ / AdminPassw0rd): tablas, botón Bloquear con nombre que incluye la cuenta, SUPPORT ve “solo lectura”.

## Fuera de alcance

Cumplimiento legal WCAG completo, lectores de pantalla móviles, transcripciones, idiomas distintos de `es`.
