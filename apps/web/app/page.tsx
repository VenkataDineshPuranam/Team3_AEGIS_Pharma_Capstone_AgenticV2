"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { StatCard } from "@/components/StatCard";
import { getQueue, listRuns, type QueueEntry, type RunResult } from "@/lib/api";
import { useRole } from "@/components/RoleProvider";
import { WORKFLOW_HREF, WORKFLOW_LABEL } from "@/lib/labels";
import type { Workflow } from "@/lib/api";

export default function HomePage() {
  const { role } = useRole();
  const [queue, setQueue] = useState<QueueEntry[]>([]);
  const [recent, setRecent] = useState<RunResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [q, r] = await Promise.all([getQueue(), listRuns()]);
      setQueue(q);
      setRecent(r.slice(0, 5));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 8000);
    return () => clearInterval(id);
  }, [refresh]);

  const atRisk = queue.filter((e) => e.hitl_deadline && new Date(e.hitl_deadline).getTime() - Date.now() < 4 * 3600000);

  return (
    <AppShell title={`Home — ${role.label}`}>
      {error && (
        <div className="mb-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error} — is the Orchestrator API running?
        </div>
      )}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="My pending" value={queue.length} />
        <StatCard label="Clocks at risk" value={atRisk.length} tone={atRisk.length ? "warn" : "good"} />
        <StatCard label="Role" value={role.requesterOnly ? "Requester" : "Approver"} />
        <StatCard label="Decision support" value="On" sub="Never a terminal action" />
      </div>
      <div className="mb-8 flex flex-wrap gap-3 text-sm">
        {(Object.keys(WORKFLOW_LABEL) as Workflow[]).map((w) => (
          <Link
            key={w}
            href={WORKFLOW_HREF[w]}
            className="rounded border border-line bg-white px-3 py-2 hover:border-navy/40"
          >
            {WORKFLOW_LABEL[w]} workspace
          </Link>
        ))}
        <Link href="/inbox" className="rounded bg-navy px-3 py-2 text-white">
          Open inbox
        </Link>
      </div>
      <h2 className="mb-2 text-sm font-semibold text-navy">Recent runs</h2>
      <ul className="space-y-1 text-sm">
        {recent.map((r) => (
          <li key={r.run_id}>
            <Link className="font-mono text-batch hover:underline" href={`/runs/${r.run_id}`}>
              {r.run_id}
            </Link>{" "}
            <span className="text-muted">
              {WORKFLOW_LABEL[r.workflow]} · {r.status}
              {r.abstention_reason === "hitl_timeout" ? " — No decision was made; resubmit." : ""}
            </span>
          </li>
        ))}
        {recent.length === 0 && <li className="text-muted">No history yet.</li>}
      </ul>
    </AppShell>
  );
}
