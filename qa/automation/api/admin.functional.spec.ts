import { BRUNO_CHECKING } from "../framework/config";
import { parseError } from "../framework/errors";
import { expect, test } from "../framework/fixtures";
import { uniqueCents } from "../framework/money";
import { provisionFundedCustomer, registerAndLogin } from "../framework/provision";

test("ADMIN lista usuarios e indicadores @regression @critical", async ({ api, seedAdmin }) => {
  const users = await api.admin.listUsers(seedAdmin.access_token);
  expect(users.some((item) => item.role === "ADMIN")).toBe(true);
  expect(users.some((item) => item.role === "CUSTOMER")).toBe(true);
  const indicators = await api.admin.indicators(seedAdmin.access_token);
  expect(indicators.users).toBeGreaterThanOrEqual(users.length);
  expect(indicators.accounts).toBeGreaterThan(0);
});

test("ADMIN bloquea una cuenta y el titular ya no origina @regression @critical", async ({
  api,
  seedAdmin,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const blocked = await api.admin.updateAccount(seedAdmin.access_token, funded.account.id, "BLOCKED");
  expect(blocked.status).toBe("BLOCKED");
  const rejected = await api.transfers.create(funded.session.access_token, {
    source_account_id: funded.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount,
    currency: "ARS",
  });
  expect(rejected.status).toBe("REJECTED");
  expect(rejected.rejection_reason).toBe("SOURCE_NOT_ACTIVE");
  const restored = await api.admin.updateAccount(seedAdmin.access_token, funded.account.id, "ACTIVE");
  expect(restored.status).toBe("ACTIVE");
});

test("ADMIN consulta operaciones y traza reducida @regression", async ({
  api,
  seedAdmin,
  customerDraft,
}) => {
  const amount = uniqueCents();
  const funded = await provisionFundedCustomer(api, customerDraft, amount);
  const transfer = await api.transfers.create(funded.session.access_token, {
    source_account_id: funded.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount,
    currency: "ARS",
  });
  const operations = await api.admin.operations(seedAdmin.access_token);
  expect(operations.transfers.some((item) => item.id === transfer.id)).toBe(true);
  const trace = await api.admin.operationTrace(seedAdmin.access_token, transfer.id);
  expect(trace.id).toBe(transfer.id);
  expect(trace.status).toBe("COMPLETED");
  expect(trace.correlation_id).toBeTruthy();
});

test("SUPPORT consulta pero no muta cuentas ni roles @regression @critical", async ({
  api,
  seedSupport,
  customerDraft,
}) => {
  const created = await registerAndLogin(api, customerDraft);
  const users = await api.admin.listUsers(seedSupport.access_token);
  expect(users.some((item) => item.email === customerDraft.email)).toBe(true);
  const mutateAccount = await api.admin.updateAccountRaw(
    seedSupport.access_token,
    created.account.id,
    "BLOCKED",
  );
  expect(mutateAccount.status()).toBe(403);
  const mutateUser = await api.admin.updateUserRaw(seedSupport.access_token, created.user.id, {
    role: "ADMIN",
  });
  expect(mutateUser.status()).toBe(403);
});

test("CUSTOMER no entra a administración @regression @critical", async ({ api, customerDraft }) => {
  const created = await registerAndLogin(api, customerDraft);
  const users = await api.admin.listUsersRaw(created.session.access_token);
  expect(users.status()).toBe(403);
  const operations = await api.admin.operationsRaw(created.session.access_token);
  expect(operations.status()).toBe(403);
  const error = await parseError(users);
  expect(error.detail.toLowerCase()).toMatch(/support|administrator/);
});

test("ADMIN puede asignar rol SUPPORT a un cliente de laboratorio @regression", async ({
  api,
  seedAdmin,
  customerDraft,
}) => {
  const created = await registerAndLogin(api, customerDraft);
  const updated = await api.admin.updateUser(seedAdmin.access_token, created.user.id, {
    role: "SUPPORT",
  });
  expect(updated.role).toBe("SUPPORT");
  const money = await api.transfers.createRaw(created.session.access_token, {
    source_account_id: created.account.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 100,
    currency: "ARS",
  });
  expect(money.status()).toBe(403);
});
