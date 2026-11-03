import { LOGIN_MAX_ATTEMPTS } from "../framework/config";
import { parseError } from "../framework/errors";
import { expect, test } from "../framework/fixtures";
import { registerAndLogin } from "../framework/provision";

test("email duplicado responde 409 @regression @critical", async ({ api, customerDraft }) => {
  await api.auth.register(customerDraft);
  const again = await api.auth.registerRaw(customerDraft);
  expect(again.status()).toBe(409);
  const error = await parseError(again);
  expect(error.detail.toLowerCase()).toContain("email");
});

test("contraseña débil no registra @regression @critical", async ({ api, customerDraft }) => {
  const response = await api.auth.registerRaw({
    email: customerDraft.email,
    password: "corta",
    fullName: customerDraft.fullName,
  });
  expect(response.status()).toBe(422);
});

test("login inválido no revela si falló el correo o la clave @regression @critical", async ({
  api,
  customerDraft,
}) => {
  await api.auth.register(customerDraft);
  const unknown = await api.auth.loginRaw("nobody-unknown@finbank.test", "WrongPassw0rd");
  const wrong = await api.auth.loginRaw(customerDraft.email, "WrongPassw0rd");
  expect(unknown.status()).toBe(401);
  expect(wrong.status()).toBe(401);
  const unknownError = await parseError(unknown);
  const wrongError = await parseError(wrong);
  expect(unknownError.detail).toBe(wrongError.detail);
  expect(unknownError.detail.toLowerCase()).not.toContain("email");
  expect(unknownError.detail.toLowerCase()).not.toContain("password");
});

test("lockout temporal tras intentos fallidos @regression @critical", async ({
  api,
  customerDraft,
}) => {
  await api.auth.register(customerDraft);
  for (let attempt = 0; attempt < LOGIN_MAX_ATTEMPTS - 1; attempt += 1) {
    const failed = await api.auth.loginRaw(customerDraft.email, "WrongPassw0rd");
    expect(failed.status()).toBe(401);
  }
  const locked = await api.auth.loginRaw(customerDraft.email, "WrongPassw0rd");
  expect(locked.status()).toBe(423);
  const stillLocked = await api.auth.loginRaw(customerDraft.email, customerDraft.password);
  expect(stillLocked.status()).toBe(423);
  const error = await parseError(stillLocked);
  expect(error.detail.toLowerCase()).toContain("locked");
});

test("logout revoca el refresh token @regression @critical", async ({ api, customerDraft }) => {
  await registerAndLogin(api, customerDraft);
  const refreshed = await api.auth.refresh();
  expect(refreshed.status()).toBe(200);
  const logout = await api.auth.logout();
  expect(logout.status()).toBe(200);
  const rejected = await api.auth.refresh();
  expect(rejected.status()).toBe(401);
});

test("refresh sin cookie falla @regression", async ({ api }) => {
  const response = await api.auth.refresh();
  expect(response.status()).toBe(401);
});

test("recuperación de un solo uso cambia la contraseña @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const created = await registerAndLogin(api, customerDraft);
  const requested = await api.auth.recovery(customerDraft.email);
  expect(requested.status()).toBe(200);
  const notifications = await api.auth.notifications(created.session.access_token);
  const reset = notifications.find((item) => item.template === "auth.password_reset");
  expect(reset).toBeTruthy();
  const token = reset?.payload.token;
  expect(typeof token).toBe("string");
  const nextPassword = "Recovered1!x";
  const confirm = await api.auth.confirmRecovery(String(token), nextPassword);
  expect(confirm.status()).toBe(200);
  const replay = await api.auth.confirmRecovery(String(token), "Another12!x");
  expect(replay.status()).toBe(401);
  const oldLogin = await api.auth.loginRaw(customerDraft.email, customerDraft.password);
  expect(oldLogin.status()).toBe(401);
  const nextLogin = await api.auth.login(customerDraft.email, nextPassword);
  expect(nextLogin.user.email).toBe(customerDraft.email);
});

test("el titular actualiza el perfil y ve actividad @regression", async ({ api, customerDraft }) => {
  const created = await registerAndLogin(api, customerDraft);
  const updated = await api.auth.updateProfile(created.session.access_token, {
    full_name: "QA Perfil Actualizado",
    phone: "1100000001",
  });
  expect(updated.full_name).toBe("QA Perfil Actualizado");
  expect(updated.phone).toBe("1100000001");
  const activity = await api.auth.activity(created.session.access_token);
  expect(activity.some((item) => item.action === "login")).toBe(true);
});
