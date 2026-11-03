# Riesgos aceptados — laboratorio HTTP

| Hallazgo típico | Por qué se acepta |
| --- | --- |
| Cookie Without Secure Flag | El stack local es `http://web`. `secure=True` solo si `APP_ENV=prod`. |
| Strict-Transport-Security ausente | No hay TLS en Compose de desarrollo. |
| CSP `style-src 'unsafe-inline'` | Hoja de estilos de la SPA; no hay JS inline. Gate ZAP solo falla en High/Critical. |
| Server version header (nginx) | Mitigado con `server_tokens off`; ZAP puede seguir viendo `nginx` en algunos assets. |
| Contenido estático cacheable | JS/CSS versionados; el HTML lleva `Cache-Control: no-store`. |
| COEP ausente | No hay COOP/COEP en el lab; no hay credenciales de terceros. |
| Modern Web Application (info) | SPA esperada; el spider no ejecuta el JS de login. |
