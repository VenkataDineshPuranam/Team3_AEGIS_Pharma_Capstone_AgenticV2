"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api";

export interface Resource<T> {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
  /** When the currently-held data was fetched -- Phase 23's "stale" state. */
  fetchedAt: Date | null;
  refresh: () => void;
}

/**
 * Fetch-on-mount, optionally poll, always cancel.
 *
 * Three things this handles that an inline useEffect + fetch typically does not:
 *
 *  1. Cancellation. Every request gets an AbortSignal tied to the effect, so a filter
 *     changed twice in quick succession cannot have its first (slower) response arrive
 *     last and overwrite the second.
 *  2. Stale-while-refreshing. A poll keeps the previous data on screen instead of
 *     flashing a skeleton every interval, and exposes `fetchedAt` so the UI can say how
 *     old what you are looking at is.
 *  3. Error persistence. A failed poll does not wipe good data off the screen; the error
 *     is surfaced alongside it.
 */
export function useApiResource<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  deps: unknown[],
  options: { pollMs?: number; enabled?: boolean } = {},
): Resource<T> {
  const { pollMs, enabled = true } = options;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(enabled);
  const [fetchedAt, setFetchedAt] = useState<Date | null>(null);
  const [nonce, setNonce] = useState(0);

  // The fetcher is typically an inline arrow function, so it is a new identity on every
  // render. Holding it in a ref keeps it out of the effect's dependency list -- otherwise
  // the effect would re-run every render and poll continuously.
  const fetcherRef = useRef(fetcher);
  // Standard "latest ref" sync: written during render so the effect below always calls
  // the newest fetcher without needing it in its dependency array.
  // eslint-disable-next-line react-hooks/refs
  fetcherRef.current = fetcher;

  const refresh = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    // `enabled` is handled in the returned value below rather than by setting state here
    // -- this effect simply does nothing while disabled, so there is no state transition
    // for it to synchronize.
    if (!enabled) return;

    const controller = new AbortController();
    let cancelled = false;

    async function load(isPoll: boolean) {
      if (!isPoll) setLoading(true);
      try {
        const result = await fetcherRef.current(controller.signal);
        if (cancelled) return;
        setData(result);
        setError(null);
        setFetchedAt(new Date());
      } catch (e) {
        if (cancelled || (e instanceof DOMException && e.name === "AbortError")) return;
        // Keep whatever data is already on screen. A transient poll failure should show a
        // warning, not blank the page an approver is reading.
        setError(e instanceof ApiError ? e : new ApiError(String(e), 0));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load(false);

    let timer: ReturnType<typeof setInterval> | undefined;
    if (pollMs) timer = setInterval(() => load(true), pollMs);

    return () => {
      cancelled = true;
      controller.abort();
      if (timer) clearInterval(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce, pollMs, enabled]);

  return { data, error, loading: enabled && loading, fetchedAt, refresh };
}

/**
 * Pause polling while the tab is hidden.
 *
 * A dashboard left open overnight in a background tab otherwise issues thousands of
 * requests nobody will read (Phase 27: repeated API calls, polling).
 */
export function useVisiblePolling(intervalMs: number): number | undefined {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const onChange = () => setVisible(document.visibilityState === "visible");
    onChange();
    document.addEventListener("visibilitychange", onChange);
    return () => document.removeEventListener("visibilitychange", onChange);
  }, []);

  return visible ? intervalMs : undefined;
}
