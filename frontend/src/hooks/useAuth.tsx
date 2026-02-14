import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from "react";
import { fetchMe, login as loginRequest, register as registerRequest } from "../lib/api";
import type { User } from "../types";

const STORAGE_KEY = "provider_ops_token";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  registerAndLogin: (email: string, password: string) => Promise<void>;
  refreshUser: () => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const profile = await fetchMe(token);
      setUser(profile);
    } catch {
      logout();
    }
  }, [logout, token]);

  useEffect(() => {
    const run = async () => {
      setIsLoading(true);
      await refreshUser();
      setIsLoading(false);
    };
    void run();
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string) => {
    const accessToken = await loginRequest(email, password);
    localStorage.setItem(STORAGE_KEY, accessToken);
    setToken(accessToken);
    const profile = await fetchMe(accessToken);
    setUser(profile);
  }, []);

  const registerAndLogin = useCallback(
    async (email: string, password: string) => {
      await registerRequest(email, password);
      await login(email, password);
    },
    [login]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      registerAndLogin,
      refreshUser,
      logout
    }),
    [token, user, isLoading, login, registerAndLogin, refreshUser, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }
  return context;
}
