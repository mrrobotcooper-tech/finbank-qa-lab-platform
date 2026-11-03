import { Pool, type QueryResultRow } from "pg";

import { qaConfig } from "./config";

export type LedgerRow = {
  direction: string;
  amount: string | number;
  currency: string;
  account_id: string;
  operation_type: string;
  balance_after: string | number;
};

export type AuditRow = {
  actor_user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  before_state: Record<string, unknown> | null;
  after_state: Record<string, unknown> | null;
  correlation_id: string;
  created_at: Date;
};

export type ReconciliationRow = {
  available_balance: string | number;
  held_balance: string | number;
  ledger_net: string | number;
};

function asInt(value: string | number): number {
  return typeof value === "number" ? value : Number.parseInt(value, 10);
}

export function createQaPool(): Pool {
  return new Pool({ connectionString: qaConfig.databaseUrl, max: 4 });
}

export async function sqlQuery<T extends QueryResultRow>(
  pool: Pool,
  text: string,
  params: unknown[] = [],
): Promise<T[]> {
  const result = await pool.query<T>(text, params);
  return result.rows;
}

export async function ledgerForOperation(pool: Pool, operationId: string): Promise<LedgerRow[]> {
  return sqlQuery<LedgerRow>(
    pool,
    `SELECT direction, amount, currency, account_id::text, operation_type, balance_after
     FROM ledger_entries
     WHERE operation_id = $1
     ORDER BY direction`,
    [operationId],
  );
}

export async function auditForEntity(
  pool: Pool,
  entityId: string,
  action?: string,
): Promise<AuditRow[]> {
  if (action) {
    return sqlQuery<AuditRow>(
      pool,
      `SELECT actor_user_id::text, action, entity_type, entity_id::text, before_state, after_state,
              correlation_id, created_at
       FROM audit_events
       WHERE entity_id = $1 AND action = $2
       ORDER BY created_at ASC`,
      [entityId, action],
    );
  }
  return sqlQuery<AuditRow>(
    pool,
    `SELECT actor_user_id::text, action, entity_type, entity_id::text, before_state, after_state,
            correlation_id, created_at
     FROM audit_events
     WHERE entity_id = $1
     ORDER BY created_at ASC`,
    [entityId],
  );
}

export async function reconcileAccount(
  pool: Pool,
  accountId: string,
): Promise<ReconciliationRow> {
  const rows = await sqlQuery<ReconciliationRow>(
    pool,
    `SELECT a.available_balance,
            a.held_balance,
            COALESCE(SUM(CASE WHEN l.direction = 'CREDIT' THEN l.amount ELSE -l.amount END), 0) AS ledger_net
     FROM accounts a
     LEFT JOIN ledger_entries l ON l.account_id = a.id
     WHERE a.id = $1
     GROUP BY a.id, a.available_balance, a.held_balance`,
    [accountId],
  );
  const row = rows[0];
  if (!row) {
    throw new Error(`No hay cuenta ${accountId} para reconciliar`);
  }
  return row;
}

export function money(value: string | number): number {
  return asInt(value);
}

export async function assertReaderCannotMutateAudit(pool: Pool): Promise<string> {
  try {
    await pool.query("UPDATE audit_events SET action = action WHERE false");
    await pool.query(
      `INSERT INTO audit_events (actor_user_id, action, entity_type, entity_id, before_state, after_state, correlation_id)
       VALUES (NULL, 'qa.forbidden', 'probe', '00000000-0000-0000-0000-000000000000', NULL, NULL, 'qa')`,
    );
    return "unexpected-write";
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    const code =
      typeof cause === "object" && cause !== null && "code" in cause
        ? String((cause as { code: unknown }).code)
        : "";
    if (code === "42501" || /permission denied|read-only|must be owner/i.test(message)) {
      return "denied";
    }
    throw cause;
  }
}
