import { useEffect, useState, type FormEvent } from "react";

import { ApiError, apiFetch, newIdempotencyKey } from "../api/client";
import type { Account, Payment } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { formatMoney, toCents } from "../lib/money";

export function PaymentsPage() {
  const { token } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountId, setAccountId] = useState("");
  const [payee, setPayee] = useState("AYSA");
  const [amount, setAmount] = useState("50.00");
  const [paymentType, setPaymentType] = useState("SERVICE");
  const [result, setResult] = useState<Payment | null>(null);
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
        items[0];
      if (preferred) {
        setAccountId(preferred.id);
      }
    });
  }, [token]);

  const account = accounts.find((item) => item.id === accountId);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token || !account) {
      return;
    }
    setPending(true);
    setError(null);
    setResult(null);
    try {
      const created = await apiFetch<Payment>("/api/v1/payments", {
        method: "POST",
        token,
        headers: { "Idempotency-Key": newIdempotencyKey() },
        body: {
          account_id: account.id,
          amount: toCents(amount),
          currency: account.currency,
          payment_type: paymentType,
          payee,
        },
      });
      setResult(created);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo pagar");
    } finally {
      setPending(false);
    }
  }

  return (
    <article>
      <h1>Pago de servicios</h1>
      <p className="lead">
        El mock aprueba salvo que el destinatario sea <code>REJECT</code>.
      </p>
      <form className="form-grid" onSubmit={onSubmit} data-testid="payment-form">
        <label>
          Cuenta
          <select
            data-testid="payment-account"
            value={accountId}
            onChange={(event) => setAccountId(event.target.value)}
          >
            {accounts.map((item) => (
              <option key={item.id} value={item.id}>
                {item.account_number} · {formatMoney(item.available_balance, item.currency)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tipo
          <select
            data-testid="payment-type"
            value={paymentType}
            onChange={(event) => setPaymentType(event.target.value)}
          >
            <option value="SERVICE">Servicio</option>
            <option value="CARD">Tarjeta</option>
            <option value="INVOICE">Factura</option>
          </select>
        </label>
        <label>
          Destinatario
          <input
            data-testid="payment-payee"
            value={payee}
            onChange={(event) => setPayee(event.target.value)}
            required
          />
        </label>
        <label>
          Importe
          <input
            data-testid="payment-amount"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            required
          />
        </label>
        {error ? (
          <p role="alert" className="alert" data-testid="payment-error">
            {error}
          </p>
        ) : null}
        {result ? (
          <p role="status" data-testid="payment-result">
            Estado: {result.status}
            {result.rejection_reason ? ` (${result.rejection_reason})` : ""}
          </p>
        ) : null}
        <button
          className="button"
          type="submit"
          disabled={pending || !account}
          data-testid="payment-submit"
        >
          Pagar
        </button>
      </form>
    </article>
  );
}
