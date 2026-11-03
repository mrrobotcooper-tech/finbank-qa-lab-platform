# Charter — sesión y lockout

**ID:** EXP-AUTH-001  
**Tiempo:** 40 min  
**Misión:** explorar login fallido, 423, refresh y logout concurrente.

## Ideas

- 5 intentos malos (`LOGIN_MAX_ATTEMPTS`) y el sexto
- Login bueno durante lockout
- Dos pestañas: logout en una, transfer en la otra
- Recovery con token de notificación en `APP_ENV=dev`
- Cookie refresh HttpOnly: no debe leerse desde JS

## Notas de sesión

_(sesión)_
