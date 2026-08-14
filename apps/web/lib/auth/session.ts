/**
 * The authenticated session -- a tiny external store over localStorage, same pattern as
 * OperatorContext's old one (useSyncExternalStore, no hydration mismatch). This is what
 * replaced OperatorContext's free-text "claimed identity": a token issued by
 * POST /api/auth/login, resolved server-side on every request by services/api/auth.py's
 * `require_user`. lib/api/client.ts reads this module directly (not through React) so it
 * can attach the Authorization header without a circular dependency on a React context.
 */

export interface Session {
  token: string;
  user_id: string;
  display_name: string;
  role: string;
  expires_at: string;
}

const STORAGE_KEY = "aegis.session";

let cached: Session | null = null;
let hydrated = false;
const listeners = new Set<() => void>();

function readStorage(): Session | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (typeof parsed?.token !== "string") return null;
    return parsed as Session;
  } catch {
    return null;
  }
}

export function subscribe(onStoreChange: () => void) {
  listeners.add(onStoreChange);
  return () => listeners.delete(onStoreChange);
}

export function getSnapshot(): Session | null {
  if (!hydrated) {
    cached = readStorage();
    hydrated = true;
  }
  return cached;
}

export function getServerSnapshot(): Session | null {
  return null;
}

export function setSession(next: Session | null): void {
  cached = next;
  hydrated = true;
  try {
    if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Private browsing / quota. Auth still works for this tab's lifetime via `cached`.
  }
  for (const listener of listeners) listener();
}

/** Read outside React (e.g. from lib/api/client.ts) without the hook's render binding. */
export function currentToken(): string | null {
  return getSnapshot()?.token ?? null;
}

/** Called by client.ts when the API reports a session is no longer valid (401). */
export function clearSessionOnUnauthorized(): void {
  if (getSnapshot() !== null) setSession(null);
}
