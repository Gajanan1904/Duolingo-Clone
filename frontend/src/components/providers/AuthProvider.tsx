"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { api } from "@/services/api";

interface AuthContextType {
  authenticated: boolean;
  loading: boolean;
  user: any;
}

const AuthContext = createContext<AuthContextType>({
  authenticated: false,
  loading: true,
  user: null,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    let isMounted = true;

    async function initSession() {
      try {
        const res = await api.ensureSession();
        if (isMounted) {
          setAuthenticated(res.authenticated);
          setUser(res.user);
        }
      } catch (err) {
        console.error("Failed to initialize session:", err);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    initSession();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <AuthContext.Provider value={{ authenticated, loading, user }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
