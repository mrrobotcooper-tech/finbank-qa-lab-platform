import { BRUNO_CHECKING } from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { uniqueCustomer } from "../framework/factory";
import { registerAndLogin } from "../framework/provision";

test("NFR-SEC-003 endpoints de dinero exigen autenticación @security @critical", async ({ api }) => {
  const accounts = await api.http.get("/api/v1/accounts");
  expect(accounts.status()).toBe(401);
  const transfers = await api.transfers.createRaw(undefined, {
    source_account_id: "00000000-0000-0000-0000-000000000001",
    destination_account_number: BRUNO_CHECKING,
    amount: 100,
    currency: "ARS",
  });
  expect(transfers.status()).toBe(401);
  const admin = await api.admin.listUsersRaw(undefined);
  expect(admin.status()).toBe(401);
});

test("FR-ADM-005 NFR-SEC-004 SUPPORT recibe 403 al mutar o mover dinero @security @critical @seed", async ({
  api,
  seedSupport,
  seedCustomer,
}) => {
  const accounts = await api.accounts.list(seedCustomer.access_token);
  const source = accounts[0];
  expect(source).toBeTruthy();
  const transfer = await api.transfers.createRaw(seedSupport.access_token, {
    source_account_id: source!.id,
    destination_account_number: BRUNO_CHECKING,
    amount: 100,
    currency: "ARS",
  });
  expect(transfer.status()).toBe(403);
  const mutate = await api.admin.updateAccountRaw(seedSupport.access_token, source!.id, "BLOCKED");
  expect(mutate.status()).toBe(403);
  const role = await api.admin.updateUserRaw(seedSupport.access_token, seedCustomer.user.id, {
    role: "ADMIN",
  });
  expect(role.status()).toBe(403);
});

test("NFR-SEC-004 CUSTOMER no administra @security @critical", async ({ api, customerDraft }) => {
  const created = await registerAndLogin(api, customerDraft);
  const users = await api.admin.listUsersRaw(created.session.access_token);
  expect(users.status()).toBe(403);
});

test("NFR-SEC-003 un token basura no autentica @security @critical", async ({ api }) => {
  const response = await api.http.get("/api/v1/me", { token: "not-a-jwt" });
  expect(response.status()).toBe(401);
});

test("FR-AUD-003 no existe GET de auditoría @security @critical", async ({ api, seedAdmin }) => {
  const anon = await api.http.get("/api/v1/admin/audit");
  expect(anon.status()).toBe(404);
  const asAdmin = await api.http.get("/api/v1/admin/audit", { token: seedAdmin.access_token });
  expect(asAdmin.status()).toBe(404);
  const stranger = await registerAndLogin(api, uniqueCustomer("audit"));
  const asCustomer = await api.http.get("/api/v1/admin/audit", {
    token: stranger.session.access_token,
  });
  expect(asCustomer.status()).toBe(404);
});
