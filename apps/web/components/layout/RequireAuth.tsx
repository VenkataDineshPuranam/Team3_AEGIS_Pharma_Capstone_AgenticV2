"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { AppShell } from "./AppShell";
import { useAuth } from "./AuthContext";

/**
 * Gates every route except /login behind a live session. This is a UX convenience, not
 * the enforcement point -- services/api/auth.py's `require_user` and
 * user_store.approver_string_for are what actually reject an unauthorized request. A
 * client that bypassed this component entirely would still get 401/403s from the API.
 *
 * The redirect itself is a navigation side effect (not derived render state), so it runs
 * in an effect -- the documented exception to this app's usual "adjust state during
 * render" preference, which applies to local setState, not to triggering navigation.
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { session } = useAuth();
  const authRequired = pathname !== "/login";

  useEffect(() => {
    if (authRequired && !session) {
      const next = pathname && pathname !== "/" ? `?next=${encodeURIComponent(pathname)}` : "";
      router.replace(`/login${next}`);
    }
  }, [authRequired, session, pathname, router]);

  if (!authRequired) return <>{children}</>;
  if (!session) return null;
  return <AppShell>{children}</AppShell>;
}
