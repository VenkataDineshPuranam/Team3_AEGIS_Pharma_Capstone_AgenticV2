"use client";

import { useEffect, useState } from "react";
import { getDashboard, type DashboardResponse, type Workflow } from "@/lib/api";
import { WORKFLOW_LABEL } from "@/lib/labels";
import { StatCard } from "./StatCard";

export function ObservabilityPanel() {
  const [filter, setFilter] = useState<Workflow | "all">("all");
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getDashboard(filter === "all" ? undefined : filter)
      .then((d) => !cancelled && setData(d))
      .catch((e) => !cancelled && setError(e instanceof Error ? e.message : "Unknown error"));
    return () => {
      cancelled = true;
    };
  }, [filter]);

  return (
    <div>
      <div className="mb-6 flex gap-2 text-sm">
        {(["all", "batch_review", "pv_intake", "supply_planning"] as const).map((w) => (
          <button
            key={w}
            type="button"
            onClick={() => setFilter(w)}
            className={`rounded-full border px-3 py-1 ${
              filter === w ? "border-navy bg-navy text-white" : "border-line text-muted"
            }`}
          >
            {w === "all" ? "All workflows" : WORKFLOW_LABEL[w]}
          </button>
        ))}
      </div>
      {error && (
        <div className="mb-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error}
        </div>
      )}
      {!data && !error && <p className="text-sm text-muted">Loading…</p>}
      {data && (
        <div className="space-y-8">
          <section>
            <h2 className="mb-2 text-sm font-semibold text-muted">Cost</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <StatCard label="Runs" value={data.cost.run_count} />
              <StatCard label="Mean tokens/run" value={data.cost.mean_tokens_per_run?.toFixed(0) ?? "—"} />
              <StatCard label="p95 tokens/run" value={data.cost.p95_tokens_per_run?.toFixed(0) ?? "—"} />
              <StatCard label="Mean LLM calls/run" value={data.cost.mean_llm_calls_per_run?.toFixed(2) ?? "—"} />
            </div>
          </section>
          <section>
            <h2 className="mb-2 text-sm font-semibold text-muted">Guardrail trips</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <StatCard label="Total runs" value={data.guardrail_trip.run_count} />
              <StatCard
                label="Blocked"
                value={data.guardrail_trip.blocked_count}
                tone={data.guardrail_trip.blocked_count > 0 ? "warn" : "good"}
              />
              <StatCard
                label="Blocked rate"
                value={
                  data.guardrail_trip.blocked_rate != null
                    ? `${(data.guardrail_trip.blocked_rate * 100).toFixed(1)}%`
                    : "—"
                }
              />
            </div>
          </section>
          <section>
            <h2 className="mb-2 text-sm font-semibold text-muted">Cache (Redis)</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <StatCard label="Hits" value={data.cache.hits ?? "—"} tone="good" />
              <StatCard label="Misses" value={data.cache.misses ?? "—"} />
              <StatCard
                label="Hit rate"
                value={data.cache.hit_rate != null ? `${(data.cache.hit_rate * 100).toFixed(1)}%` : "—"}
              />
            </div>
          </section>
          <section>
            <h2 className="mb-2 text-sm font-semibold text-muted">
              Terminal states ({data.terminal_states.run_count} runs)
            </h2>
            <div className="mb-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {Object.entries(data.terminal_states.by_terminal_state).map(([state, count]) => (
                <StatCard
                  key={state}
                  label={state}
                  value={count}
                  tone={state === "blocked" ? "danger" : state === "completed" ? "good" : "neutral"}
                />
              ))}
            </div>
            <h3 className="mb-2 text-xs font-semibold text-muted">By abstention reason</h3>
            <table className="w-full text-sm">
              <tbody>
                {Object.entries(data.terminal_states.by_abstention_reason).map(([reason, count]) => (
                  <tr key={reason} className="border-t border-line">
                    <td className="py-1.5 text-muted">
                      {reason}
                      {reason === "hitl_timeout" ? " — No decision was made; resubmit." : ""}
                    </td>
                    <td className="py-1.5 text-right font-mono">{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}
    </div>
  );
}
