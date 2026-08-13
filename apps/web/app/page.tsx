"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { decideRun, getQueue, type QueueEntry, type Workflow } from "@/lib/api";
import { PendingItemCard } from "@/components/PendingItemCard";

const POLL_MS = 4000;

export default function ApproverDashboard() {
  const [entries, setEntries] = useState<QueueEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Workflow | "all">("all");

  const refresh = useCallback(async () => {
    try {
      const data = await getQueue(filter === "all" ? undefined : filter);
      setEntries(data);
      setError(null);
    } catch (e) {
      setError(
        e instanceof Error
          ? `${e.message} -- is the Orchestrator API running at NEXT_PUBLIC_API_URL?`
          : "Unknown error",
      );
    }
  }, [filter]);

  useEffect(() => {
    // refresh() is async -- its setState calls happen after the awaited fetch resolves,
    // not synchronously during this effect's execution, so this is the standard
    // fetch-on-mount-then-poll pattern, not the synchronous-setState anti-pattern the
    // rule is meant to catch (react-hooks/set-state-in-effect false-positives on this
    // shape since it can't see through the async boundary).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  async function handleDecide(
    runId: string,
    decision:
      | { action: "approved" | "rejected" | "veto" }
      | { action: "approved" | "rejected"; leg: "planning" | "quality" },
  ) {
    const entry = entries?.find((e) => e.run_id === runId);
    if (!entry) return;
    await decideRun(runId, { workflow: entry.workflow, ...decision });
    await refresh();
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
            Approver Dashboard
          </h1>
          <p className="text-sm text-slate-500">
            Pending human-in-the-loop decisions across all three governed workflows.
          </p>
        </div>
        <nav className="flex gap-4 text-sm">
          <Link className="text-blue-600 hover:underline" href="/submit">
            Submit run
          </Link>
          <Link className="text-blue-600 hover:underline" href="/observability">
            Observability
          </Link>
        </nav>
      </header>

      <div className="mb-4 flex gap-2 text-sm">
        {(["all", "batch_review", "pv_intake", "supply_planning"] as const).map((w) => (
          <button
            key={w}
            onClick={() => setFilter(w)}
            className={`rounded-full px-3 py-1 border ${
              filter === w
                ? "bg-slate-900 text-white border-slate-900 dark:bg-slate-50 dark:text-slate-900"
                : "border-slate-300 text-slate-600 dark:border-slate-700 dark:text-slate-300"
            }`}
          >
            {w === "all" ? "All" : w}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {entries === null && !error && (
        <p className="text-sm text-slate-400">Loading queue…</p>
      )}

      {entries !== null && entries.length === 0 && (
        <p className="text-sm text-slate-400">
          Nothing pending. Submit a run to see it appear here.
        </p>
      )}

      <div className="space-y-3">
        {entries?.map((entry) => (
          <PendingItemCard key={entry.run_id} entry={entry} onDecide={handleDecide} />
        ))}
      </div>
    </main>
  );
}
