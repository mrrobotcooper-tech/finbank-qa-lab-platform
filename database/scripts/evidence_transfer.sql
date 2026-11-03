-- Consultas de evidencia (Fase 6). Las corre el framework; no hay GET /audit.
-- $1 = transfer_id  $2 = source_account_id

-- FR-TRF-008 doble asiento
SELECT direction, amount, currency, account_id, operation_type, balance_after
FROM ledger_entries
WHERE operation_id = $1
ORDER BY direction;

-- FR-ACCT-006 saldo vs ledger
SELECT a.available_balance,
       a.held_balance,
       COALESCE(SUM(CASE WHEN l.direction = 'CREDIT' THEN l.amount ELSE -l.amount END), 0) AS ledger_net
FROM accounts a
LEFT JOIN ledger_entries l ON l.account_id = a.id
WHERE a.id = $2
GROUP BY a.id, a.available_balance, a.held_balance;

-- FR-TRF-010 / FR-AUD-001 sin API
SELECT actor_user_id, action, entity_type, entity_id, before_state, after_state,
       correlation_id, created_at
FROM audit_events
WHERE entity_id = $1
  AND action = 'transfer.created';
