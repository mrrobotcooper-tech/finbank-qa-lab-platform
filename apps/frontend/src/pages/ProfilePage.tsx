import { useEffect, useState, type FormEvent } from "react";

import { ApiError, apiFetch } from "../api/client";
import type { User } from "../api/types";
import { useAuth } from "../auth/AuthContext";

export function ProfilePage() {
  const { token, user } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [phone, setPhone] = useState(user?.phone ?? "");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFullName(user?.full_name ?? "");
    setPhone(user?.phone ?? "");
  }, [user]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setError(null);
    setMessage(null);
    try {
      await apiFetch<User>("/api/v1/me", {
        method: "PATCH",
        token,
        body: { full_name: fullName, phone },
      });
      setMessage("Perfil actualizado");
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo guardar");
    }
  }

  return (
    <article>
      <h1 data-testid="profile-heading">Perfil</h1>
      <p className="meta">{user?.email}</p>
      <form className="form-grid" onSubmit={onSubmit} data-testid="profile-form">
        <label>
          Nombre
          <input
            data-testid="profile-full-name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            required
          />
        </label>
        <label>
          Teléfono
          <input
            data-testid="profile-phone"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
          />
        </label>
        {error ? (
          <p role="alert" className="alert" data-testid="profile-error">
            {error}
          </p>
        ) : null}
        {message ? (
          <p role="status" data-testid="profile-status">
            {message}
          </p>
        ) : null}
        <button className="button" type="submit" data-testid="profile-submit">
          Guardar
        </button>
      </form>
    </article>
  );
}
