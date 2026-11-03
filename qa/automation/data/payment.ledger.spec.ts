import { expect, test } from "../framework/fixtures";
import { uniqueCents } from "../framework/money";
import { provisionFundedCustomer } from "../framework/provision";
import { createQaPool, ledgerForOperation, money, reconcileAccount } from "../framework/sql";

test("FR-PAY-001 pago COMPLETED deja un único débito reconciliable @regression @critical @data", async ({
  api,
  customerDraft,
}) => {
  const pool = createQaPool();
  try {
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
    const entries = await ledgerForOperation(pool, payment.id);
    expect(entries).toHaveLength(1);
    expect(entries[0]?.direction).toBe("DEBIT");
    expect(money(entries[0]?.amount ?? 0)).toBe(amount);
    const recon = await reconcileAccount(pool, funded.account.id);
    expect(money(recon.available_balance)).toBe(money(recon.ledger_net) - money(recon.held_balance));
  } finally {
    await pool.end();
  }
});

test("FR-PAY-004 pago REJECT no escribe ledger @regression @critical @data", async ({
  api,
  customerDraft,
}) => {
  const pool = createQaPool();
  try {
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
    const entries = await ledgerForOperation(pool, payment.id);
    expect(entries).toHaveLength(0);
    const recon = await reconcileAccount(pool, funded.account.id);
    expect(money(recon.available_balance)).toBe(amount);
  } finally {
    await pool.end();
  }
});
