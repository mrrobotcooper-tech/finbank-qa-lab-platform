import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { apiFetch } from "../api/client";
import type { TokenResponse, User } from "../api/types";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  const apply = useCallback((payload: TokenResponse) => {
    setUser(payload.user);
    setToken(payload.access_token);
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const payload = await apiFetch<TokenResponse>("/api/v1/auth/refresh", { method: "POST" });
        if (!cancelled) {
          apply(payload);
        }
      } catch {
        if (!cancelled) {
          setUser(null);
          setToken(null);
        }
      } finally {
        if (!cancelled) {
          setReady(true);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [apply]);

  const login = useCallback(
    async (email: string, password: string) => {
      const payload = await apiFetch<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: { email, password },
      });
      apply(payload);
    },
    [apply],
  );

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    await apiFetch("/api/v1/auth/register", {
      method: "POST",
      body: { email, password, full_name: fullName },
    });
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiFetch("/api/v1/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
      setToken(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, token, ready, login, register, logout }),
    [user, token, ready, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {  // eslint-disable-line react-refresh/only-export-components
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth requiere AuthProvider");
  }
  return context;
}
