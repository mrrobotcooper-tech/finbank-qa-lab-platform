import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await register(email, password, fullName);
      navigate("/login");
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo registrar");
    } finally {
      setPending(false);
    }
  }

  return (
    <article>
      <h1>Registro</h1>
      <p className="lead">Se crea una caja de ahorro/cuenta corriente ARS con saldo 0.</p>
      <form className="form-grid" onSubmit={onSubmit} data-testid="register-form">
        <label>
          Nombre
          <input
            data-testid="register-full-name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            required
          />
        </label>
        <label>
          Correo
          <input
            data-testid="register-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          Contraseña
          <input
            data-testid="register-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        {error ? (
          <p role="alert" className="alert" data-testid="register-error">
            {error}
          </p>
        ) : null}
        <button className="button" type="submit" disabled={pending} data-testid="register-submit">
          Crear cuenta
        </button>
      </form>
      <p>
        <Link to="/login">Ya tengo usuario</Link>
      </p>
    </article>
  );
}
