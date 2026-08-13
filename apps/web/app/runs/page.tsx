"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { StatusChip } from "@/components/StatusChip";
import { WorkflowBadge } from "@/components/WorkflowBadge";
import { listRuns, type RunResult, type Workflow } from "@/lib/api";
import { WORKFLOW_LABEL, statusLabel } from "@/lib/labels";

export default function HistoryPage() {
  const [filter, setFilter] = useState<Workflow | "all">("all");
  const [status, setStatus] = useState<string>("all");
  const [runs, setRuns] = useState<RunResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listRuns({
      workflow: filter === "all" ? undefined : filter,
      status: status === "all" ? undefined : status,
    })
      .then(setRuns)
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, [filter, status]);

  return (
    <AppShell title="Run history">
      {error && (
        <div className="mb-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error}
        </div>
      )}
      <div className="mb-4 flex flex-wrap gap-2 text-sm">
        {(["all", "batch_review", "pv_intake", "supply_planning"] as const).map((w) => (
          <button
            key={w}
            type="button"
            onClick={() => setFilter(w)}
            className={`rounded-full border px-3 py-1 ${
              filter === w ? "border-navy bg-navy text-white" : "border-line text-muted"
            }`}
          >
            {w === "all" ? "All" : WORKFLOW_LABEL[w]}
          </button>
        ))}
        {["all", "completed", "abstained", "blocked", "refused", "timed_out", "pending_approval"].map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatus(s)}
            className={`rounded-full border px-3 py-1 ${
              status === s ? "border-navy bg-navy text-white" : "border-line text-muted"
            }`}
          >
            {s === "all" ? "Any status" : statusLabel(s)}
          </button>
        ))}
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-muted">
            <th className="py-2">Run</th>
            <th>Workflow</th>
            <th>Subject</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => (
            <tr key={r.run_id} className="border-t border-line">
              <td className="py-2 font-mono">
                <Link className="text-batch hover:underline" href={`/runs/${r.run_id}`}>
                  {r.run_id}
                </Link>
              </td>
              <td>
                <WorkflowBadge workflow={r.workflow} />
              </td>
              <td className="font-mono">{r.subject_id ?? "—"}</td>
              <td>
                <StatusChip status={r.status} />
                {r.abstention_reason === "hitl_timeout" && (
                  <span className="ml-2 text-xs text-amber">No decision was made; resubmit.</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {runs.length === 0 && <p className="mt-4 text-sm text-muted">No runs recorded.</p>}
    </AppShell>
  );
}
