import { useCallback, useEffect, useState } from "react";

import { ApiError, apiFetch } from "../api/client";
import type { Account, User } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { formatMoney } from "../lib/money";
import { usePageTitle } from "../lib/usePageTitle";

type Indicators = {
  users: number;
  accounts: number;
  completed_transfers: number;
};

export function AdminPage() {
  usePageTitle("Administración");
  const { token, user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [indicators, setIndicators] = useState<Indicators | null>(null);
  const [error, setError] = useState<string | null>(null);
  const canMutate = user?.role === "ADMIN";

  const load = useCallback(async () => {
    if (!token) {
      return;
    }
    const [nextUsers, nextAccounts, nextIndicators] = await Promise.all([
      apiFetch<User[]>("/api/v1/admin/users", { token }),
      apiFetch<Account[]>("/api/v1/accounts", { token }),
      apiFetch<Indicators>("/api/v1/admin/indicators", { token }),
    ]);
    setUsers(nextUsers);
    setAccounts(nextAccounts);
    setIndicators(nextIndicators);
  }, [token]);

  useEffect(() => {
    void load().catch((cause) => {
      setError(cause instanceof ApiError ? cause.message : "No se pudo cargar el panel");
    });
  }, [load]);

  async function setAccountStatus(accountId: string, status: string) {
    if (!token) {
      return;
    }
    setError(null);
    try {
      await apiFetch(`/api/v1/admin/accounts/${accountId}`, {
        method: "PATCH",
        token,
        body: { status },
      });
      await load();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo actualizar la cuenta");
    }
  }

  return (
    <article>
      <h1 data-testid="admin-heading">Administración</h1>
      {indicators ? (
        <p className="meta" data-testid="admin-indicators">
          Usuarios {indicators.users} · Cuentas {indicators.accounts} · Transferencias completadas{" "}
          {indicators.completed_transfers}
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="alert" data-testid="admin-error">
          {error}
        </p>
      ) : null}
      <h2>Usuarios</h2>
      <table className="status-table" data-testid="admin-users">
        <caption className="visually-hidden">Usuarios del laboratorio</caption>
        <thead>
          <tr>
            <th>Correo</th>
            <th>Rol</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {users.map((item) => (
            <tr key={item.id}>
              <td>{item.email}</td>
              <td>{item.role}</td>
              <td>{item.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Cuentas</h2>
      <table className="status-table" data-testid="admin-accounts">
        <caption className="visually-hidden">Cuentas y acciones administrativas</caption>
        <thead>
          <tr>
            <th>Número</th>
            <th>Saldo</th>
            <th>Estado</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((account) => (
            <tr key={account.id} data-testid={`admin-account-${account.account_number}`}>
              <td>{account.account_number}</td>
              <td>{formatMoney(account.available_balance, account.currency)}</td>
              <td data-testid={`admin-account-status-${account.account_number}`}>
                {account.status}
              </td>
              <td>
                {canMutate ? (
                  <button
                    className="button button--small"
                    type="button"
                    data-testid={`admin-toggle-${account.account_number}`}
                    onClick={() =>
                      void setAccountStatus(
                        account.id,
                        account.status === "BLOCKED" ? "ACTIVE" : "BLOCKED",
                      )
                    }
                  >
                    {account.status === "BLOCKED" ? "Desbloquear" : "Bloquear"}
                  </button>
                ) : (
                  "solo lectura"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  );
}
