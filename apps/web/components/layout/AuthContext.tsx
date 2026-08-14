"use client";

import { createContext, useCallback, useContext, useMemo, useSyncExternalStore, type ReactNode } from "react";
import { ApiError, login as apiLogin, logout as apiLogout } from "@/lib/api";
import { getServerSnapshot, getSnapshot, setSession, subscribe, type Session } from "@/lib/auth/session";

interface AuthState {
  session: Session | null;
  signIn: (userId: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthCtx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const session = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const signIn = useCallback(async (userId: string, password: string) => {
    const result = await apiLogin(userId, password);
    setSession(result);
  }, []);

  const signOut = useCallback(async () => {
    try {
      await apiLogout();
    } catch (e) {
      // Logging out locally must succeed even if the network call fails (e.g. the
      // session already expired server-side) -- the point is the client stops sending
      // the stale token, not that the server round-trip succeeds.
      if (!(e instanceof ApiError)) throw e;
    } finally {
      setSession(null);
    }
  }, []);

  const value = useMemo(() => ({ session, signIn, signOut }), [session, signIn, signOut]);
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
