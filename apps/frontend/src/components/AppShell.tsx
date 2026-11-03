import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const { user, logout } = useAuth();
  const isStaff = user?.role === "ADMIN" || user?.role === "SUPPORT";

  return (
    <>
      <a className="skip-link" href="#contenido" data-testid="skip-link">
        Saltar al contenido
      </a>
      <header className="site-header">
        <div className="site-header__inner">
          <p className="brand">
            <span className="brand__name">FinBank</span>
            <span className="brand__tag">laboratorio QA · datos ficticios</span>
          </p>
          <nav aria-label="Principal">
            <ul className="nav-list">
              <li>
                <NavLink to="/" end data-testid="nav-home">
                  Inicio
                </NavLink>
              </li>
              {user ? (
                <>
                  <li>
                    <NavLink to="/accounts" data-testid="nav-accounts">
                      Cuentas
                    </NavLink>
                  </li>
                  <li>
                    <NavLink to="/transfers" data-testid="nav-transfers">
                      Transferir
                    </NavLink>
                  </li>
                  <li>
                    <NavLink to="/payments" data-testid="nav-payments">
                      Pagos
                    </NavLink>
                  </li>
                  <li>
                    <NavLink to="/profile" data-testid="nav-profile">
                      Perfil
                    </NavLink>
                  </li>
                  {isStaff ? (
                    <li>
                      <NavLink to="/admin" data-testid="nav-admin">
                        Admin
                      </NavLink>
                    </li>
                  ) : null}
                </>
              ) : (
                <li>
                  <NavLink to="/login" data-testid="nav-login">
                    Ingresar
                  </NavLink>
                </li>
              )}
              <li>
                <NavLink to="/status">Estado</NavLink>
              </li>
              {user ? (
                <li>
                  <button
                    className="nav-logout"
                    type="button"
                    data-testid="nav-logout"
                    onClick={() => void logout()}
                  >
                    Salir
                  </button>
                </li>
              ) : null}
            </ul>
          </nav>
        </div>
      </header>
      <main id="contenido" className="site-main" tabIndex={-1}>
        {children}
      </main>
      <footer className="site-footer">
        <div className="site-footer__inner">
          <p>FinBank no es un banco real. No opera dinero ni datos personales auténticos.</p>
        </div>
      </footer>
    </>
  );
}
