import { expect, test } from "../../framework/fixtures";
import { uniqueCents } from "../../framework/money";
import { provisionFundedCustomer } from "../../framework/provision";

test("el dashboard muestra la cuenta fondeada del cliente único @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  accountsPage,
  page,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await expect(accountsPage.accountRow(funded.account.account_number)).toBeVisible();
  await accountsPage.accountRow(funded.account.account_number).locator("a").click();
  await expect(page.getByTestId("account-balance")).toBeVisible();
  await expect(page.getByTestId("movements-table")).toBeVisible();
});
