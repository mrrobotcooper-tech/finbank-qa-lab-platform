import {
  ANA_CHECKING,
  BRUNO_BLOCKED,
  BRUNO_CHECKING,
  PER_OPERATION_LIMIT,
} from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { uniqueCustomer } from "../framework/factory";
import { uniqueCents } from "../framework/money";
import { parseError } from "../framework/errors";
import { provisionFundedCustomer, registerAndLogin } from "../framework/provision";

test("transferencia entre clientes completa y queda consultable @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const created = await api.transfers.create(funded.session.access_token, {
    source_account_id: funded.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount,
    currency: "ARS",
  });
  expect(created.status).toBe("COMPLETED");
  expect(created.id).toBeTruthy();
  expect(created.amount).toBe(amount);
  const fetched = await api.transfers.get(funded.session.access_token, created.id);
  expect(fetched.id).toBe(created.id);
  expect(fetched.status).toBe("COMPLETED");
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(0);
  const movements = await api.accounts.movements(funded.session.access_token, funded.account.id);
  expect(movements.some((item) => item.operation_id === created.id && item.direction === "DEBIT")).toBe(
    true,
  );
});

test("fondos insuficientes rechazan sin debitar @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const created = await registerAndLogin(api, customerDraft);
  const before = created.account.available_balance;
  const rejected = await api.transfers.create(created.session.access_token, {
    source_account_id: created.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 500,
    currency: "ARS",
  });
  expect(rejected.status).toBe("REJECTED");
  expect(rejected.rejection_reason).toBe("INSUFFICIENT_FUNDS");
  const after = await api.accounts.get(created.session.access_token, created.account.id);
  expect(after.available_balance).toBe(before);
});

test("la misma Idempotency-Key no duplica el movimiento @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const key = crypto.randomUUID();
  const payload = {
    source_account_id: funded.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount,
    currency: "ARS",
  };
  const first = await api.transfers.create(funded.session.access_token, payload, key);
  const second = await api.transfers.create(funded.session.access_token, payload, key);
  expect(second.id).toBe(first.id);
  expect(first.status).toBe("COMPLETED");
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(0);
});

test("moneda distinta se rechaza @regression @critical", async ({ api, customerDraft }) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const rejected = await api.transfers.create(funded.session.access_token, {
    source_account_id: funded.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount,
    currency: "USD",
  });
  expect(rejected.status).toBe("REJECTED");
  expect(rejected.rejection_reason).toBe("CURRENCY_MISMATCH");
  const source = await api.accounts.get(funded.session.access_token, funded.account.id);
  expect(source.available_balance).toBe(amount);
});

test("exceso del límite por operación se rechaza sin movimiento @regression @critical @seed", async ({
  api,
  seedCustomer,
}) => {
  const accounts = await api.accounts.list(seedCustomer.access_token);
  const source = accounts.find((item) => item.account_number === ANA_CHECKING);
  expect(source).toBeTruthy();
  const before = source!.available_balance;
  const rejected = await api.transfers.create(seedCustomer.access_token, {
    source_account_id: source!.id,
    destination_account_number: BRUNO_CHECKING,
    amount: PER_OPERATION_LIMIT + 1,
    currency: "ARS",
  });
  expect(rejected.status).toBe("REJECTED");
  expect(rejected.rejection_reason).toBe("PER_OPERATION_LIMIT");
  const after = await api.accounts.get(seedCustomer.access_token, source!.id);
  expect(after.available_balance).toBe(before);
});

test("cuenta BLOCKED no origina transferencias @regression @critical @seed", async ({
  api,
  seedBruno,
}) => {
  const accounts = await api.accounts.list(seedBruno.access_token);
  const blocked = accounts.find((item) => item.account_number === BRUNO_BLOCKED);
  expect(blocked).toBeTruthy();
  const before = blocked!.available_balance;
  const rejected = await api.transfers.create(seedBruno.access_token, {
    source_account_id: blocked!.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 100,
    currency: "ARS",
  });
  expect(rejected.status).toBe("REJECTED");
  expect(rejected.rejection_reason).toBe("SOURCE_NOT_ACTIVE");
  const after = await api.accounts.get(seedBruno.access_token, blocked!.id);
  expect(after.available_balance).toBe(before);
});

test("un cliente no usa la cuenta de otro como origen @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const owner = await registerAndLogin(api, customerDraft);
  const stranger = await registerAndLogin(api, uniqueCustomer("src"));
  const response = await api.transfers.createRaw(stranger.session.access_token, {
    source_account_id: owner.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 100,
    currency: "ARS",
  });
  expect(response.status()).toBe(403);
  const error = await parseError(response);
  expect(error.detail.toLowerCase()).toContain("source");
});

test("un cliente no lee la transferencia de otro @regression @critical", async ({
  api,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const created = await api.transfers.create(funded.session.access_token, {
    source_account_id: funded.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount,
    currency: "ARS",
  });
  const stranger = await registerAndLogin(api, uniqueCustomer("spy"));
  const response = await api.transfers.getRaw(stranger.session.access_token, created.id);
  expect(response.status()).toBe(403);
});

test("SUPPORT no puede mover dinero @regression @critical", async ({ api, seedSupport, seedCustomer }) => {
  const accounts = await api.accounts.list(seedCustomer.access_token);
  const source = accounts.find((item) => item.account_number === ANA_CHECKING);
  const response = await api.transfers.createRaw(seedSupport.access_token, {
    source_account_id: source!.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 100,
    currency: "ARS",
  });
  expect(response.status()).toBe(403);
});

test("importe cero es error de contrato @regression", async ({ api, customerDraft }) => {
  const created = await registerAndLogin(api, customerDraft);
  const response = await api.transfers.createRaw(created.session.access_token, {
    source_account_id: created.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 0,
    currency: "ARS",
  });
  expect(response.status()).toBe(422);
});
