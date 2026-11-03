import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { AppShell } from "../components/AppShell";
import { AccountDetailPage } from "../pages/AccountDetailPage";
import { AccountsPage } from "../pages/AccountsPage";
import { AdminPage } from "../pages/AdminPage";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../pages/LoginPage";
import { PaymentsPage } from "../pages/PaymentsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { RecoveryPage } from "../pages/RecoveryPage";
import { RegisterPage } from "../pages/RegisterPage";
import { StatusPage } from "../pages/StatusPage";
import { TransferPage } from "../pages/TransferPage";

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  if (!ready) {
    return <p role="status">Cargando sesión…</p>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function RequireStaff({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  if (!ready) {
    return <p role="status">Cargando sesión…</p>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.role !== "ADMIN" && user.role !== "SUPPORT") {
    return <Navigate to="/accounts" replace />;
  }
  return children;
}

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/recovery" element={<RecoveryPage />} />
        <Route path="/status" element={<StatusPage />} />
        <Route
          path="/accounts"
          element={
            <RequireAuth>
              <AccountsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/accounts/:accountId"
          element={
            <RequireAuth>
              <AccountDetailPage />
            </RequireAuth>
          }
        />
        <Route
          path="/transfers"
          element={
            <RequireAuth>
              <TransferPage />
            </RequireAuth>
          }
        />
        <Route
          path="/payments"
          element={
            <RequireAuth>
              <PaymentsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/profile"
          element={
            <RequireAuth>
              <ProfilePage />
            </RequireAuth>
          }
        />
        <Route
          path="/admin"
          element={
            <RequireStaff>
              <AdminPage />
            </RequireStaff>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
