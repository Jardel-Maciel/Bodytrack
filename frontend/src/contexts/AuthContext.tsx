import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import * as authService from "@/services/authService";
import type { AuthUser, ProfileUpdateInput } from "@/services/authService";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  loginWithPassword: (email: string, password: string) => Promise<void>;
  registerAndLogin: (input: { email: string; password: string; name: string }) => Promise<void>;
  updateProfile: (input: ProfileUpdateInput) => Promise<AuthUser>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STORAGE_KEY = "bodytrack.auth";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Ao carregar o app, se já existe um token salvo, confirma que ele
  // ainda é válido chamando /auth/me (em vez de confiar cegamente no
  // que está no localStorage — o token pode ter expirado).
  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      setLoading(false);
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setToken(parsed.token);
      authService
        .me()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem(STORAGE_KEY);
          setToken(null);
        })
        .finally(() => setLoading(false));
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setLoading(false);
    }
  }, []);

  const persist = (newToken: string, newUser: AuthUser) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: newToken, user: newUser }));
  };

  const loginWithPassword = async (email: string, password: string) => {
    const { access_token } = await authService.login(email, password);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: access_token, user: null }));
    setToken(access_token);
    const me = await authService.me();
    persist(access_token, me);
  };

  const registerAndLogin = async (input: { email: string; password: string; name: string }) => {
    await authService.register(input);
    await loginWithPassword(input.email, input.password);
  };

  const updateProfile = async (input: ProfileUpdateInput) => {
    const updated = await authService.updateMe(input);
    setUser(updated);
    if (token) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, user: updated }));
    }
    return updated;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      loading,
      loginWithPassword,
      registerAndLogin,
      updateProfile,
      logout,
    }),
    [user, token, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de <AuthProvider>");
  return ctx;
}
