import { BRUNO_CHECKING } from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { uniqueCents } from "../framework/money";
import { provisionFundedCustomer } from "../framework/provision";
import {
  assertReaderCannotMutateAudit,
  auditForEntity,
  createQaPool,
  ledgerForOperation,
  money,
  reconcileAccount,
} from "../framework/sql";

test("FR-TRF-008 FR-TRF-010 FR-AUD-001 transferencia API afirma ledger y audit_events sin GET de auditoría @regression @critical @data", async ({
  api,
  customerDraft,
}) => {
  const pool = createQaPool();
  try {
    const amount = uniqueCents();
    const funded = await provisionFundedCustomer(api, customerDraft, amount);
    const transfer = await api.transfers.create(funded.session.access_token, {
      source_account_id: funded.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount,
      currency: "ARS",
    });
    expect(transfer.status).toBe("COMPLETED");

    const forbidden = await api.http.get("/api/v1/admin/audit");
    expect(forbidden.status()).toBe(404);

    const entries = await ledgerForOperation(pool, transfer.id);
    expect(entries).toHaveLength(2);
    const debit = entries.find((row) => row.direction === "DEBIT");
    const credit = entries.find((row) => row.direction === "CREDIT");
    expect(money(debit?.amount ?? 0)).toBe(amount);
    expect(money(credit?.amount ?? 0)).toBe(amount);
    expect(debit?.account_id).toBe(funded.account.id);
    expect(credit?.account_id).toBe(transfer.destination_account_id);

    const source = await reconcileAccount(pool, funded.account.id);
    expect(money(source.available_balance)).toBe(money(source.ledger_net) - money(source.held_balance));
    expect(money(source.available_balance)).toBe(0);

    const destination = await reconcileAccount(pool, transfer.destination_account_id);
    expect(money(destination.available_balance)).toBe(
      money(destination.ledger_net) - money(destination.held_balance),
    );

    const events = await auditForEntity(pool, transfer.id, "transfer.created");
    expect(events).toHaveLength(1);
    expect(events[0]?.actor_user_id).toBe(funded.user.id);
    expect(events[0]?.entity_type).toBe("transfer");
    expect(events[0]?.correlation_id).toBe(transfer.correlation_id);
    expect(events[0]?.after_state).toMatchObject({ status: "COMPLETED", amount });
    expect(events[0]?.created_at).toBeTruthy();
  } finally {
    await pool.end();
  }
});

test("FR-AUD-002 el lector QA no puede mutar audit_events @regression @critical @data", async () => {
  const pool = createQaPool();
  try {
    const outcome = await assertReaderCannotMutateAudit(pool);
    expect(outcome).toBe("denied");
  } finally {
    await pool.end();
  }
});
