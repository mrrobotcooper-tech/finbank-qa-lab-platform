import { useState, type FormEvent } from "react";

import { ApiError, apiFetch } from "../api/client";

export function RecoveryPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await apiFetch("/api/v1/auth/recovery", { method: "POST", body: { email } });
      setMessage("Si el correo existe, el worker encoló un aviso ficticio.");
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo pedir el reset");
    }
  }

  return (
    <article>
      <h1 data-testid="recovery-heading">Recuperar contraseña</h1>
      <form className="form-grid" onSubmit={onSubmit} data-testid="recovery-form">
        <label>
          Correo
          <input
            data-testid="recovery-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        {error ? (
          <p role="alert" className="alert" data-testid="recovery-error">
            {error}
          </p>
        ) : null}
        {message ? (
          <p role="status" data-testid="recovery-status">
            {message}
          </p>
        ) : null}
        <button className="button" type="submit" data-testid="recovery-submit">
          Enviar
        </button>
      </form>
    </article>
  );
}
