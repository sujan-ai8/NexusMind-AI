import React, { createContext, useContext, useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { User } from "@/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => Promise<void>;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem("nexusmind_user");
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem("nexusmind_token");
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function verifySession() {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await apiRequest<User>("/auth/me");
        setUser(currentUser);
        localStorage.setItem("nexusmind_user", JSON.stringify(currentUser));
      } catch (err) {
        console.warn("Session verification expired or failed:", err);
        localStorage.removeItem("nexusmind_token");
        localStorage.removeItem("nexusmind_user");
        setUser(null);
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    }

    verifySession();
  }, [token]);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem("nexusmind_token", newToken);
    localStorage.setItem("nexusmind_user", JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = async () => {
    try {
      if (token) {
        await apiRequest("/auth/logout", { method: "POST" });
      }
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem("nexusmind_token");
      localStorage.removeItem("nexusmind_user");
      localStorage.removeItem("nexusmind_active_workspace_id");
      setToken(null);
      setUser(null);
    }
  };

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
    localStorage.setItem("nexusmind_user", JSON.stringify(updatedUser));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

