import { BRUNO_CHECKING } from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { uniqueCents } from "../framework/money";
import { uniqueCustomer } from "../framework/factory";
import { provisionFundedCustomer, registerAndLogin } from "../framework/provision";
import { createQaPool, ledgerForOperation, money, reconcileAccount } from "../framework/sql";

test("FR-ACCT-006 el saldo persistido coincide con el neto del ledger @regression @critical @data", async ({
  api,
  customerDraft,
}) => {
  const pool = createQaPool();
  try {
    const amount = uniqueCents();
    const funded = await provisionFundedCustomer(api, customerDraft, amount);
    const before = await reconcileAccount(pool, funded.account.id);
    expect(money(before.available_balance)).toBe(money(before.ledger_net) - money(before.held_balance));

    const transfer = await api.transfers.create(funded.session.access_token, {
      source_account_id: funded.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount,
      currency: "ARS",
    });
    expect(transfer.status).toBe("COMPLETED");

    const after = await reconcileAccount(pool, funded.account.id);
    expect(money(after.available_balance)).toBe(0);
    expect(money(after.available_balance)).toBe(money(after.ledger_net) - money(after.held_balance));
  } finally {
    await pool.end();
  }
});

test("FR-TRF-006 FR-TRF-009 replay idempotente no duplica asientos y el rechazo no escribe ledger @regression @critical @data", async ({
  api,
  customerDraft,
}) => {
  const pool = createQaPool();
  try {
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
    const replay = await api.transfers.create(funded.session.access_token, payload, key);
    expect(replay.id).toBe(first.id);
    const posted = await ledgerForOperation(pool, first.id);
    expect(posted).toHaveLength(2);

    const broke = await registerAndLogin(api, uniqueCustomer("nsf"));
    const rejected = await api.transfers.create(broke.session.access_token, {
      source_account_id: broke.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount: 900,
      currency: "ARS",
    });
    expect(rejected.status).toBe("REJECTED");
    const empty = await ledgerForOperation(pool, rejected.id);
    expect(empty).toHaveLength(0);
    const recon = await reconcileAccount(pool, broke.account.id);
    expect(money(recon.available_balance)).toBe(0);
  } finally {
    await pool.end();
  }
});
