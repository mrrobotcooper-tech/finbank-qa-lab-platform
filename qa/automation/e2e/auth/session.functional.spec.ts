import { qaConfig } from "../../framework/config";
import { expect, test } from "../../framework/fixtures";
import { registerAndLogin } from "../../framework/provision";

test("credenciales inválidas muestran error genérico @regression @critical", async ({ loginPage }) => {
  await loginPage.goto();
  await loginPage.login("nobody-missing@finbank.test", "WrongPassw0rd");
  await expect(loginPage.error()).toBeVisible();
  const message = (await loginPage.error().textContent()) ?? "";
  expect(message.toLowerCase()).not.toContain("password");
  expect(message.toLowerCase()).not.toContain("email");
});

test("logout vuelve al login y oculta la navegación de cuentas @regression @critical", async ({
  loginPage,
  accountsPage,
  page,
}) => {
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.ana.email, qaConfig.seed.ana.password);
  await accountsPage.waitForLoaded();
  await page.getByTestId("nav-logout").click();
  await expect(page.getByTestId("login-form")).toBeVisible();
  await expect(page.getByTestId("nav-accounts")).toHaveCount(0);
});

test("recuperación UI confirma el aviso sin filtrar existencia @regression", async ({
  recoveryPage,
  customerDraft,
}) => {
  await recoveryPage.goto();
  await recoveryPage.submit(customerDraft.email);
  await expect(recoveryPage.status()).toBeVisible();
  await expect(recoveryPage.status()).toContainText("correo");
});

test("el titular edita el perfil desde la UI @regression", async ({
  api,
  customerDraft,
  loginPage,
  profilePage,
}) => {
  await registerAndLogin(api, customerDraft);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await profilePage.goto();
  await profilePage.save("Nombre QA UI");
  await expect(profilePage.status()).toHaveText("Perfil actualizado");
});
