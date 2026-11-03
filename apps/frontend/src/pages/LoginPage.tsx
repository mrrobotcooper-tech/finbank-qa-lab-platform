import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { usePageTitle } from "../lib/usePageTitle";

export function LoginPage() {
  usePageTitle("Ingresar");
  const { user, ready, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("ana@finbank.test");
  const [password, setPassword] = useState("Customer1!");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (ready && user) {
    return <Navigate to="/accounts" replace />;
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await login(email, password);
      navigate("/accounts");
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo iniciar sesión");
    } finally {
      setPending(false);
    }
  }

  return (
    <article>
      <h1>Ingresar</h1>
      <p className="lead">Usuarios de laboratorio. No hay dinero ni personas reales.</p>
      <form className="form-grid" onSubmit={onSubmit} data-testid="login-form">
        <label>
          Correo
          <input
            data-testid="login-email"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label>
          Contraseña
          <input
            data-testid="login-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        {error ? (
          <p role="alert" className="alert" data-testid="login-error">
            {error}
          </p>
        ) : null}
        <button className="button" type="submit" disabled={pending} data-testid="login-submit">
          {pending ? "Ingresando…" : "Ingresar"}
        </button>
      </form>
      <p>
        <Link to="/register">Crear cuenta</Link>
        {" · "}
        <Link to="/recovery">Recuperar contraseña</Link>
      </p>
      <section className="panel">
        <h2>Cuentas demo</h2>
        <table className="status-table">
          <caption className="visually-hidden">Cuentas demo del laboratorio</caption>
          <thead>
            <tr>
              <th>Rol</th>
              <th>Correo</th>
              <th>Clave</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Cliente</td>
              <td>ana@finbank.test</td>
              <td>Customer1!</td>
            </tr>
            <tr>
              <td>Cliente</td>
              <td>bruno@finbank.test</td>
              <td>Customer1!</td>
            </tr>
            <tr>
              <td>Admin</td>
              <td>admin@finbank.test</td>
              <td>AdminPassw0rd</td>
            </tr>
          </tbody>
        </table>
      </section>
    </article>
  );
}
