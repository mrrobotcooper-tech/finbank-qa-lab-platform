import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiFetch } from "../api/client";
import type { Account } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { formatMoney } from "../lib/money";
import { usePageTitle } from "../lib/usePageTitle";

export function AccountsPage() {
  usePageTitle("Cuentas");
  const { token } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    void apiFetch<Account[]>("/api/v1/accounts", { token })
      .then(setAccounts)
      .catch((cause) => {
        setError(cause instanceof ApiError ? cause.message : "No se pudieron cargar las cuentas");
      });
  }, [token]);

  return (
    <article>
      <h1 data-testid="accounts-heading">Cuentas</h1>
      {error ? (
        <p role="alert" className="alert">
          {error}
        </p>
      ) : null}
      <table className="status-table" data-testid="accounts-table">
        <caption className="visually-hidden">Cuentas del titular</caption>
        <thead>
          <tr>
            <th>Número</th>
            <th>Tipo</th>
            <th>Moneda</th>
            <th>Saldo</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((account) => (
            <tr key={account.id} data-testid={`account-${account.account_number}`}>
              <td>
                <Link to={`/accounts/${account.id}`}>{account.account_number}</Link>
              </td>
              <td>{account.type}</td>
              <td>{account.currency}</td>
              <td>{formatMoney(account.available_balance, account.currency)}</td>
              <td>{account.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  );
}
