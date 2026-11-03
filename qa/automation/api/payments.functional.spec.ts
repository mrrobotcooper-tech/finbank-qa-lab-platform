import { expect, test } from "../framework/fixtures";
import { uniqueCents } from "../framework/money";
import { provisionFundedCustomer, registerAndLogin } from "../framework/provision";

test("pago de servicio ficticio debita la cuenta @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const payment = await api.payments.create(funded.session.access_token, {
    account_id: funded.account.id,
    amount,
    currency: "ARS",
    payment_type: "SERVICE",
    payee: "AYSA",
  });
  expect(payment.status).toBe("COMPLETED");
  expect(payment.payee).toBe("AYSA");
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(0);
  const listed = await api.payments.list(funded.session.access_token);
  expect(listed.some((item) => item.id === payment.id)).toBe(true);
  const fetched = await api.payments.get(funded.session.access_token, payment.id);
  expect(fetched.status).toBe("COMPLETED");
});

test("pago REJECT del mock no debita @regression @critical", async ({ api, customerDraft }) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const payment = await api.payments.create(funded.session.access_token, {
    account_id: funded.account.id,
    amount,
    currency: "ARS",
    payment_type: "INVOICE",
    payee: "REJECT",
  });
  expect(payment.status).toBe("REJECTED");
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(amount);
});

test("pago programado queda SCHEDULED sin debitar @regression", async ({ api, customerDraft }) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const payment = await api.payments.create(funded.session.access_token, {
    account_id: funded.account.id,
    amount,
    currency: "ARS",
    payment_type: "CARD",
    payee: "VISA-MOCK",
    scheduled_at: "2099-01-01T00:00:00Z",
  });
  expect(payment.status).toBe("SCHEDULED");
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(amount);
});

test("pago sin saldo se rechaza @regression @critical", async ({ api, customerDraft }) => {
  const created = await registerAndLogin(api, customerDraft);
  const payment = await api.payments.create(created.session.access_token, {
    account_id: created.account.id,
    amount: 250,
    currency: "ARS",
    payment_type: "SERVICE",
    payee: "AYSA",
  });
  expect(payment.status).toBe("REJECTED");
  expect(payment.rejection_reason).toBe("INSUFFICIENT_FUNDS");
});

test("idempotencia de pago no duplica el débito @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const key = crypto.randomUUID();
  const payload = {
    account_id: funded.account.id,
    amount,
    currency: "ARS",
    payment_type: "SERVICE" as const,
    payee: "EDESUR",
  };
  const first = await api.payments.create(funded.session.access_token, payload, key);
  const second = await api.payments.create(funded.session.access_token, payload, key);
  expect(second.id).toBe(first.id);
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(0);
});
