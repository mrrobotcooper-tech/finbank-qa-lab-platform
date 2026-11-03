import { expect, test } from "../framework/fixtures";
import { assertIntegerCents } from "../framework/money";

test("registro, login y listado de cuentas de un cliente nuevo @smoke @critical", async ({
  api,
  customerDraft,
}) => {
  const created = await api.auth.register(customerDraft);
  expect(created.email).toBe(customerDraft.email);
  expect(created.role).toBe("CUSTOMER");

  const session = await api.auth.login(customerDraft.email, customerDraft.password);
  expect(session.user.id).toBe(created.id);

  const me = await api.auth.me(session.access_token);
  expect(me.email).toBe(customerDraft.email);

  const accounts = await api.accounts.list(session.access_token);
  expect(accounts.length).toBeGreaterThanOrEqual(1);
  for (const account of accounts) {
    assertIntegerCents(account.available_balance);
    assertIntegerCents(account.held_balance);
  }
  expect(accounts[0]?.currency).toBe("ARS");
  expect(accounts[0]?.available_balance).toBe(0);
});

test("credenciales inválidas no emiten token @smoke @critical", async ({ api, customerDraft }) => {
  const response = await api.auth.loginRaw(customerDraft.email, "WrongPassw0rd");
  expect(response.status()).toBe(401);
});

test("el seed de Ana autentica y ve cuentas @smoke @critical @seed", async ({
  api,
  seedCustomer,
}) => {
  expect(seedCustomer.user.role).toBe("CUSTOMER");
  const accounts = await api.accounts.list(seedCustomer.access_token);
  expect(accounts.length).toBeGreaterThanOrEqual(1);
  expect(accounts.some((item) => item.account_number === "32200000000000000001")).toBe(true);
});
