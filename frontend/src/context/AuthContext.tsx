/**
 * RHOS Authentication Context.
 *
 * Provides auth state, login/logout, and token management.
 */

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { User, LoginRequest, RegisterRequest } from "../types";
import { authApi } from "../api";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem("rhos_token");
    const savedUser = localStorage.getItem("rhos_user");

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem("rhos_token");
        localStorage.removeItem("rhos_user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    const response = await authApi.login(data);
    localStorage.setItem("rhos_token", response.access_token);
    if (response.user) {
      localStorage.setItem("rhos_user", JSON.stringify(response.user));
      setUser(response.user);
    }
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    const response = await authApi.register(data);
    localStorage.setItem("rhos_token", response.access_token);
    if (response.user) {
      localStorage.setItem("rhos_user", JSON.stringify(response.user));
      setUser(response.user);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("rhos_token");
    localStorage.removeItem("rhos_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
