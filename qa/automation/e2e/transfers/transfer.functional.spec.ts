import { BRUNO_CHECKING } from "../../framework/config";
import { expect, test } from "../../framework/fixtures";
import { fromCents, uniqueCents } from "../../framework/money";
import { provisionFundedCustomer, registerAndLogin } from "../../framework/provision";

test("cliente fondeado transfiere a Bruno y ve estado COMPLETED @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  transferPage,
  accountsPage,
}) => {
  const amount = uniqueCents(200, 900);
  await provisionFundedCustomer(api, customerDraft, amount);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await transferPage.goto();
  await transferPage.submit(BRUNO_CHECKING, fromCents(amount));
  await expect(transferPage.result()).toContainText("COMPLETED");
});

test("sin saldo la UI muestra transferencia rechazada @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  transferPage,
  accountsPage,
}) => {
  await registerAndLogin(api, customerDraft);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await transferPage.goto();
  await transferPage.submit(BRUNO_CHECKING, "10.00");
  await expect(transferPage.result()).toContainText("REJECTED");
  await expect(transferPage.result()).toContainText("INSUFFICIENT_FUNDS");
});
