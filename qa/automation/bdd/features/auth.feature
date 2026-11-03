# language: es
@bdd @critical @auth
Característica: Autenticación de clientes
  Como visitante del laboratorio FinBank
  Quiero registrarme e ingresar
  Para operar con cuentas ficticias

  @FR-AUTH-001
  Escenario: registro válido crea un CUSTOMER con cuenta ARS
    Dado un email de laboratorio único
    Cuando me registro con contraseña válida
    Entonces el usuario queda con rol "CUSTOMER"
    Y puedo autenticarme y ver una cuenta ARS

  @FR-AUTH-001
  Escenario: email duplicado es conflicto
    Dado un cliente ya registrado
    Cuando intento registrarme otra vez con el mismo email
    Entonces la API responde 409

  @FR-AUTH-002
  Escenario: credenciales inválidas no emiten token
    Dado un cliente ya registrado
    Cuando intento autenticarme con una clave incorrecta
    Entonces la API responde 401
