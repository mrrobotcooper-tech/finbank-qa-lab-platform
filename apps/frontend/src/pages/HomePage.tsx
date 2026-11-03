import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <article>
      <h1>Banca digital ficticia para ingeniería de calidad</h1>
      <p className="lead">
        FinBank es el System Under Test de una plataforma de QA. La Fase 2 cubre registro, sesión,
        cuentas, transferencias, pagos mock y bloqueo administrativo. No hay dinero real.
      </p>
      <ul className="feature-list">
        <li>Ledger en PostgreSQL con saldos en centavos (bigint).</li>
        <li>JWT de 15 minutos y cookie de refresh rotativa.</li>
        <li>Pasarela y notificaciones mock: el payee <code>REJECT</code> rechaza el cobro.</li>
      </ul>
      <p className="button-row">
        <Link className="button" to="/login">
          Ingresar
        </Link>
        <Link className="button" to="/register">
          Crear cuenta
        </Link>
        <Link className="button" to="/status">
          Estado del sistema
        </Link>
      </p>
    </article>
  );
}
