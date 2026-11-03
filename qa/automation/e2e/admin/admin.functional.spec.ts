import { qaConfig } from "../../framework/config";
import { expect, test } from "../../framework/fixtures";
import { registerAndLogin } from "../../framework/provision";

test("CUSTOMER no ve Admin y /admin redirige a cuentas @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  accountsPage,
  page,
}) => {
  await registerAndLogin(api, customerDraft);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await expect(page.getByTestId("nav-admin")).toHaveCount(0);
  await page.goto("/admin");
  await accountsPage.waitForLoaded();
  await expect(page.getByTestId("admin-heading")).toHaveCount(0);
});

test("SUPPORT ve el panel en solo lectura @regression @critical @seed", async ({
  loginPage,
  adminPage,
  page,
}) => {
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.support.email, qaConfig.seed.support.password);
  await expect(page.getByTestId("nav-admin")).toBeVisible();
  await adminPage.goto();
  await expect(adminPage.heading()).toBeVisible();
  await expect(adminPage.usersTable()).toBeVisible();
  await expect(page.getByText("solo lectura").first()).toBeVisible();
});

test("ADMIN bloquea la cuenta de un cliente nuevo @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  adminPage,
  accountsPage,
  transferPage,
  page,
}) => {
  const created = await registerAndLogin(api, customerDraft);
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.admin.email, qaConfig.seed.admin.password);
  await adminPage.goto();
  await expect(adminPage.heading()).toBeVisible();
  await expect(adminPage.usersTable()).toContainText(customerDraft.email);
  await expect(adminPage.toggle(created.account.account_number)).toBeVisible();
  await adminPage.toggle(created.account.account_number).click();
  await expect(adminPage.accountStatus(created.account.account_number)).toHaveText("BLOCKED");
  await page.getByTestId("nav-logout").click();
  await expect(page.getByTestId("login-form")).toBeVisible();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await expect(accountsPage.accountRow(created.account.account_number)).toContainText("BLOCKED");
  await transferPage.goto();
  await expect(transferPage.submitButton()).toBeDisabled();
});
