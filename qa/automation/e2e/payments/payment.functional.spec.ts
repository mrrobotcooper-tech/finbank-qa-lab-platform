import { expect, test } from "../../framework/fixtures";
import { fromCents, uniqueCents } from "../../framework/money";
import { provisionFundedCustomer } from "../../framework/provision";

test("pago de servicio en UI queda COMPLETED @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  paymentPage,
  accountsPage,
}) => {
  const amount = uniqueCents(200, 900);
  await provisionFundedCustomer(api, customerDraft, amount);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await paymentPage.goto();
  await paymentPage.submit("AYSA", fromCents(amount), "SERVICE");
  await expect(paymentPage.result()).toContainText("COMPLETED");
});

test("destinatario REJECT no debita y muestra REJECTED @regression @critical", async ({
  api,
  customerDraft,
  loginPage,
  paymentPage,
  accountsPage,
}) => {
  const amount = uniqueCents(200, 900);
  await provisionFundedCustomer(api, customerDraft, amount);
  await loginPage.goto();
  await loginPage.login(customerDraft.email, customerDraft.password);
  await accountsPage.waitForLoaded();
  await paymentPage.goto();
  await paymentPage.submit("REJECT", fromCents(amount), "INVOICE");
  await expect(paymentPage.result()).toContainText("REJECTED");
});
