import { qaConfig } from "../../framework/config";
import { expect, test } from "../../framework/fixtures";

test("login de Ana muestra el dashboard de cuentas @smoke @critical @seed", async ({
  loginPage,
  accountsPage,
}) => {
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.ana.email, qaConfig.seed.ana.password);
  await accountsPage.waitForLoaded();
  await expect(accountsPage.table()).toBeVisible();
  await expect(accountsPage.accountRow("32200000000000000001")).toBeVisible();
});

test("registro UI y login llegan al dashboard @smoke @critical", async ({
  registerPage,
  loginPage,
  accountsPage,
  customerDraft,
}) => {
  await registerPage.goto();
  await registerPage.submit(customerDraft);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await expect(accountsPage.table().locator("tbody tr")).toHaveCount(1);
});
