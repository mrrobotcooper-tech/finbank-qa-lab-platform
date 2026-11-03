import { useEffect, useState, type FormEvent } from "react";

import { ApiError, apiFetch, newIdempotencyKey } from "../api/client";
import type { Account, Transfer } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { formatMoney, toCents } from "../lib/money";
import { usePageTitle } from "../lib/usePageTitle";

export function TransferPage() {
  usePageTitle("Transferencia");
  const { token } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [sourceId, setSourceId] = useState("");
  const [destination, setDestination] = useState("32200000000000000003");
  const [amount, setAmount] = useState("100.00");
  const [result, setResult] = useState<Transfer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (!token) {
      return;
    }
    void apiFetch<Account[]>("/api/v1/accounts", { token }).then((items) => {
      setAccounts(items);
      const preferred =
        items.find((item) => item.status === "ACTIVE" && item.currency === "ARS") ??
        items.find((item) => item.status === "ACTIVE");
      if (preferred) {
        setSourceId(preferred.id);
      }
    });
  }, [token]);

  const source = accounts.find((item) => item.id === sourceId);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token || !source) {
      return;
    }
    setPending(true);
    setError(null);
    setResult(null);
    try {
      const created = await apiFetch<Transfer>("/api/v1/transfers", {
        method: "POST",
        token,
        headers: { "Idempotency-Key": newIdempotencyKey() },
        body: {
          source_account_id: source.id,
          destination_account_number: destination,
          amount: toCents(amount),
          currency: source.currency,
        },
      });
      setResult(created);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo transferir");
    } finally {
      setPending(false);
    }
  }

  return (
    <article>
      <h1>Transferencia</h1>
      <p className="lead">
        Demo: la cuenta corriente ARS de Bruno es <code>32200000000000000003</code>.
      </p>
      <form className="form-grid" onSubmit={onSubmit} data-testid="transfer-form">
        <label>
          Cuenta origen
          <select
            data-testid="transfer-source"
            value={sourceId}
            onChange={(event) => setSourceId(event.target.value)}
            required
          >
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_number} · {formatMoney(account.available_balance, account.currency)}
              </option>
            ))}
          </select>
        </label>
        <label>
          CBU destino (ficticio)
          <input
            data-testid="transfer-destination"
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
            required
          />
        </label>
        <label>
          Importe
          <input
            data-testid="transfer-amount"
            inputMode="decimal"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            required
          />
        </label>
        {error ? (
          <p role="alert" className="alert" data-testid="transfer-error">
            {error}
          </p>
        ) : null}
        {result ? (
          <p role="status" data-testid="transfer-result">
            Estado: {result.status}
            {result.rejection_reason ? ` (${result.rejection_reason})` : ""}
          </p>
        ) : null}
        <button
          className="button"
          type="submit"
          disabled={pending || !source}
          data-testid="transfer-submit"
        >
          Transferir
        </button>
      </form>
    </article>
  );
}
