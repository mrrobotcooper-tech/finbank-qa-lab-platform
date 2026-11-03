import { BRUNO_CHECKING } from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { uniqueCustomer } from "../framework/factory";
import { uniqueCents } from "../framework/money";
import { provisionFundedCustomer } from "../framework/provision";
import { auditForEntity, createQaPool } from "../framework/sql";

test("FR-AUD-002 un audit previo no cambia cuando llega otro evento @regression @critical @data", async ({
  api,
  customerDraft,
}) => {
  const pool = createQaPool();
  try {
    const firstAmount = uniqueCents(130, 180);
    const first = await provisionFundedCustomer(api, customerDraft, firstAmount);
    const transfer = await api.transfers.create(first.session.access_token, {
      source_account_id: first.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount: firstAmount,
      currency: "ARS",
    });
    const original = await auditForEntity(pool, transfer.id, "transfer.created");
    expect(original).toHaveLength(1);
    const snapshot = JSON.stringify(original[0]?.after_state);

    const second = await provisionFundedCustomer(api, uniqueCustomer("aud"), uniqueCents(190, 240));
    await api.transfers.create(second.session.access_token, {
      source_account_id: second.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount: second.fundedAmount,
      currency: "ARS",
    });

    const reread = await auditForEntity(pool, transfer.id, "transfer.created");
    expect(reread).toHaveLength(1);
    expect(JSON.stringify(reread[0]?.after_state)).toBe(snapshot);
    expect(reread[0]?.created_at?.toISOString()).toBe(original[0]?.created_at?.toISOString());
  } finally {
    await pool.end();
  }
});
