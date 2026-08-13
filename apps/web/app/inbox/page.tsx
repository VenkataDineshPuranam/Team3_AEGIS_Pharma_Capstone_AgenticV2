"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { InboxList } from "@/components/InboxList";
import { getQueue, type QueueEntry, type Workflow } from "@/lib/api";

export default function InboxPage() {
  const [filter, setFilter] = useState<Workflow | "all">("all");
  const [entries, setEntries] = useState<QueueEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setEntries(await getQueue(filter === "all" ? undefined : filter));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    }
  }, [filter]);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  return (
    <AppShell title="HITL inbox">
      {error && (
        <div className="mb-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error}
        </div>
      )}
      <p className="mb-4 text-sm text-muted">
        Sorted by time-to-next-tier. Silence is never approval. PV uses a wall clock.
      </p>
      <InboxList entries={entries} filter={filter} onFilter={setFilter} />
    </AppShell>
  );
}
