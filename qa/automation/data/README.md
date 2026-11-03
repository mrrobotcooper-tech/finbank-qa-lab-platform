# Data testing

Aserciones SQL con el rol `finbank_qa_reader`. **Prohibido** `GET /api/v1/admin/audit`.

Patrón: factory HTTP → operación API → `SELECT` sobre `ledger_entries` / `audit_events` / `accounts`.

```bash
make qa-data
```
