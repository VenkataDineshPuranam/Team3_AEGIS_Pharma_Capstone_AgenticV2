"use client";

import { createContext, useCallback, useContext, useMemo, useSyncExternalStore, type ReactNode } from "react";

/**
 * The operator's CLAIMED identity and role.
 *
 * This is not authentication and it is not authorization. There is no login in this build,
 * and the backend enforces no server-side authorization (see /api/governance's
 * `authentication` block, which reports that plainly).
 *
 * What this context is for:
 *   - attaching a claimed identity to the audit record of a decision, as context
 *   - showing the operator which role's queue they are looking at
 *
 * What it must never be used for:
 *   - deciding whether an action is permitted
 *   - hiding a control as though hiding it were a security measure
 *
 * Anyone who can reach the API can call it directly with any role string. The UI
 * therefore states this openly rather than implying a control it does not have, and the
 * selector is labelled as an unverified assertion everywhere it appears.
 */

export const DOMAIN_ROLES = [
  "EU Qualified Person",
  "Global Head of Pharmacovigilance",
  "Patient Safety Representative",
  "Supply Chain VP",
  "Quality Co-Approver",
  "Compliance Reviewer",
  "Platform Operator",
] as const;

export type DomainRole = (typeof DOMAIN_ROLES)[number];

interface OperatorState {
  role: DomainRole;
  setRole: (role: DomainRole) => void;
  /** Free-text identifier recorded alongside a decision. Unverified. */
  identity: string;
  setIdentity: (identity: string) => void;
}

const OperatorCtx = createContext<OperatorState | null>(null);

const STORAGE_KEY = "aegis.operator";
const DEFAULT_SNAPSHOT: { role: DomainRole; identity: string } = {
  role: "EU Qualified Person",
  identity: "",
};

/**
 * A tiny external store over localStorage, read via useSyncExternalStore.
 *
 * This is the React-documented way to read state that lives outside React (localStorage
 * is exactly that) without a hydration mismatch: `getServerSnapshot` returns the same
 * default the server rendered, and the store only reads the real value once mounted in
 * the browser, on its own subscribe/notify cycle rather than through a setState-in-effect
 * that a naive "read on mount" implementation would need.
 */
let cached: typeof DEFAULT_SNAPSHOT = DEFAULT_SNAPSHOT;
let hydrated = false;
const listeners = new Set<() => void>();

function readStorage(): typeof DEFAULT_SNAPSHOT {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_SNAPSHOT;
    const parsed = JSON.parse(raw);
    return {
      role: DOMAIN_ROLES.includes(parsed.role) ? parsed.role : DEFAULT_SNAPSHOT.role,
      identity: typeof parsed.identity === "string" ? parsed.identity : "",
    };
  } catch {
    return DEFAULT_SNAPSHOT;
  }
}

function subscribe(onStoreChange: () => void) {
  listeners.add(onStoreChange);
  return () => listeners.delete(onStoreChange);
}

function getSnapshot() {
  if (!hydrated) {
    cached = readStorage();
    hydrated = true;
  }
  return cached;
}

function getServerSnapshot() {
  return DEFAULT_SNAPSHOT;
}

function write(next: typeof DEFAULT_SNAPSHOT) {
  cached = next;
  hydrated = true;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Private browsing / quota. The app works fine without persistence.
  }
  for (const listener of listeners) listener();
}

export function OperatorProvider({ children }: { children: ReactNode }) {
  const snapshot = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const setRole = useCallback((role: DomainRole) => write({ ...cached, role }), []);
  const setIdentity = useCallback((identity: string) => write({ ...cached, identity }), []);

  const value = useMemo(
    () => ({ role: snapshot.role, setRole, identity: snapshot.identity, setIdentity }),
    [snapshot, setRole, setIdentity],
  );

  return <OperatorCtx.Provider value={value}>{children}</OperatorCtx.Provider>;
}

export function useOperator(): OperatorState {
  const ctx = useContext(OperatorCtx);
  if (!ctx) throw new Error("useOperator must be used inside OperatorProvider");
  return ctx;
}
