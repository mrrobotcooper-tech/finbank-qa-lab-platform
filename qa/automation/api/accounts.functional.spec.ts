import { ANA_CHECKING } from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { uniqueCustomer } from "../framework/factory";
import { assertIntegerCents } from "../framework/money";
import { registerAndLogin } from "../framework/provision";

test("el cliente ve saldo entero, tipo y moneda de su cuenta @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const created = await registerAndLogin(api, customerDraft);
  expect(created.account.type).toBe("CHECKING");
  expect(created.account.currency).toBe("ARS");
  expect(created.account.status).toBe("ACTIVE");
  assertIntegerCents(created.account.available_balance);
  assertIntegerCents(created.account.held_balance);
  expect(created.account.available_balance).toBe(0);
  expect(created.account.account_number.length).toBeGreaterThanOrEqual(6);
});

test("un cliente no lee la cuenta de otro @regression @critical", async ({ api, customerDraft }) => {
  const owner = await registerAndLogin(api, customerDraft);
  const stranger = await registerAndLogin(api, uniqueCustomer("qa2"));
  const response = await api.accounts.getRaw(stranger.session.access_token, owner.account.id);
  expect(response.status()).toBe(403);
});

test("sin token no hay listado de cuentas @regression @critical", async ({ api }) => {
  const response = await api.http.get("/api/v1/accounts");
  expect(response.status()).toBe(401);
});

test("Ana seed tiene cuentas ARS y USD consultables @regression @seed", async ({
  api,
  seedCustomer,
}) => {
  const accounts = await api.accounts.list(seedCustomer.access_token);
  const ars = accounts.find((item) => item.account_number === ANA_CHECKING);
  const usd = accounts.find((item) => item.currency === "USD");
  expect(ars, "Ana debe tener cuenta ARS seed").toBeTruthy();
  expect(usd, "Ana debe tener cuenta USD seed").toBeTruthy();
  if (!ars) {
    throw new Error("missing Ana ARS account");
  }
  expect(ars.available_balance).toBeGreaterThan(0);
  const detail = await api.accounts.get(seedCustomer.access_token, ars.id);
  expect(detail.id).toBe(ars.id);
  const movements = await api.accounts.movements(seedCustomer.access_token, ars.id);
  expect(Array.isArray(movements)).toBe(true);
});
