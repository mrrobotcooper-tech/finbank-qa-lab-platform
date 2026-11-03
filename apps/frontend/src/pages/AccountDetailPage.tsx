import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, apiFetch } from "../api/client";
import type { Account, Movement } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { formatMoney } from "../lib/money";

export function AccountDetailPage() {
  const { accountId } = useParams();
  const { token } = useAuth();
  const [account, setAccount] = useState<Account | null>(null);
  const [movements, setMovements] = useState<Movement[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !accountId) {
      return;
    }
    void Promise.all([
      apiFetch<Account>(`/api/v1/accounts/${accountId}`, { token }),
      apiFetch<Movement[]>(`/api/v1/accounts/${accountId}/movements`, { token }),
    ])
      .then(([nextAccount, nextMovements]) => {
        setAccount(nextAccount);
        setMovements(nextMovements);
      })
      .catch((cause) => {
        setError(cause instanceof ApiError ? cause.message : "No se pudo cargar la cuenta");
      });
  }, [accountId, token]);

  return (
    <article>
      <p>
        <Link to="/accounts">← Cuentas</Link>
      </p>
      <h1>Detalle de cuenta</h1>
      {error ? (
        <p role="alert" className="alert">
          {error}
        </p>
      ) : null}
      {account ? (
        <section className="panel">
          <p>
            <strong>{account.account_number}</strong> · {account.type} · {account.status}
          </p>
          <p data-testid="account-balance">
            Disponible: {formatMoney(account.available_balance, account.currency)}
          </p>
        </section>
      ) : null}
      <h2>Movimientos</h2>
      <table className="status-table" data-testid="movements-table">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Dirección</th>
            <th>Importe</th>
            <th>Saldo</th>
          </tr>
        </thead>
        <tbody>
          {movements.map((item) => (
            <tr key={item.id}>
              <td>{item.operation_type}</td>
              <td>{item.direction}</td>
              <td>{formatMoney(item.amount, item.currency)}</td>
              <td>{formatMoney(item.balance_after, item.currency)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  );
}
