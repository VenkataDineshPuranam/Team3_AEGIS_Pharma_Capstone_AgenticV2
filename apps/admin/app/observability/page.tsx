"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/AdminShell";
import { StatCard } from "@/components/StatCard";
import { getDashboard, type DashboardResponse, type Workflow } from "@/lib/api";

export default function ObservabilityPage() {
  const [filter, setFilter] = useState<Workflow | "all">("all");
  const [data, setData] = useState<DashboardResponse | null>(null);
  useEffect(() => {
    getDashboard(filter === "all" ? undefined : filter).then(setData).catch(() => setData(null));
  }, [filter]);
  return (
    <AdminShell title="Observability">
      <p className="mb-4 text-sm text-muted">
        Numbers from the owned audit store and Redis counters — not LangSmith. Hosted traces are additive.
      </p>
      <div className="mb-6 flex gap-2 text-sm">
        {(["all", "batch_review", "pv_intake", "supply_planning"] as const).map((w) => (
          <button
            key={w}
            type="button"
            onClick={() => setFilter(w)}
            className={`rounded-full border px-3 py-1 ${filter === w ? "border-navy bg-navy text-white" : "border-line"}`}
          >
            {w === "all" ? "All" : w}
          </button>
        ))}
      </div>
      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard label="Runs" value={data.cost.run_count} />
            <StatCard label="Mean tokens" value={data.cost.mean_tokens_per_run?.toFixed(0) ?? "—"} />
            <StatCard label="Blocked" value={data.guardrail_trip.blocked_count} tone={data.guardrail_trip.blocked_count ? "warn" : "good"} />
            <StatCard
              label="Cache hit rate"
              value={data.cache.hit_rate != null ? `${(data.cache.hit_rate * 100).toFixed(1)}%` : "—"}
            />
          </div>
          <table className="w-full text-sm">
            <tbody>
              {Object.entries(data.terminal_states.by_terminal_state).map(([k, v]) => (
                <tr key={k} className="border-t border-line">
                  <td className="py-1.5">{k}</td>
                  <td className="text-right font-mono">{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AdminShell>
  );
}
