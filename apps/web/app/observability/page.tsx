"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getDashboard, type DashboardResponse, type Workflow } from "@/lib/api";
import { StatCard } from "@/components/StatCard";

const WORKFLOWS: (Workflow | "all")[] = ["all", "batch_review", "pv_intake", "supply_planning"];

export default function ObservabilityPage() {
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
    <main className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
            Observability
          </h1>
          <p className="text-sm text-slate-500">
            Real numbers from evidence/audit_store.sqlite3 and the Redis response cache
            (packages/observability/dashboard_data.py) -- not synthetic.
          </p>
        </div>
        <Link className="text-sm text-blue-600 hover:underline" href="/">
          ← Approver Dashboard
        </Link>
      </header>

      <div className="mb-6 flex gap-2 text-sm">
        {WORKFLOWS.map((w) => (
          <button
            key={w}
            onClick={() => setFilter(w)}
            className={`rounded-full px-3 py-1 border ${
              filter === w
                ? "bg-slate-900 text-white border-slate-900 dark:bg-slate-50 dark:text-slate-900"
                : "border-slate-300 text-slate-600 dark:border-slate-700 dark:text-slate-300"
            }`}
          >
            {w === "all" ? "All workflows" : w}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {!data && !error && <p className="text-sm text-slate-400">Loading…</p>}

      {data && (
        <div className="space-y-8">
          <section>
            <h2 className="text-sm font-semibold text-slate-500 mb-2">Cost</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <StatCard label="Runs" value={data.cost.run_count} />
              <StatCard
                label="Mean tokens/run"
                value={data.cost.mean_tokens_per_run?.toFixed(0) ?? "—"}
              />
              <StatCard
                label="p95 tokens/run"
                value={data.cost.p95_tokens_per_run?.toFixed(0) ?? "—"}
              />
              <StatCard
                label="Mean LLM calls/run"
                value={data.cost.mean_llm_calls_per_run?.toFixed(2) ?? "—"}
              />
            </div>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-slate-500 mb-2">Guardrail trips</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
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
            <h2 className="text-sm font-semibold text-slate-500 mb-2">Cache (Redis)</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <StatCard label="Hits" value={data.cache.hits ?? "—"} tone="good" />
              <StatCard label="Misses" value={data.cache.misses ?? "—"} />
              <StatCard
                label="Hit rate"
                value={data.cache.hit_rate != null ? `${(data.cache.hit_rate * 100).toFixed(1)}%` : "—"}
              />
            </div>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-slate-500 mb-2">
              Terminal states ({data.terminal_states.run_count} runs)
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
              {Object.entries(data.terminal_states.by_terminal_state).map(([state, count]) => (
                <StatCard
                  key={state}
                  label={state}
                  value={count}
                  tone={state === "blocked" ? "danger" : state === "completed" ? "good" : "neutral"}
                />
              ))}
            </div>
            <h3 className="text-xs font-semibold text-slate-400 mb-2">By abstention reason</h3>
            <table className="w-full text-sm">
              <tbody>
                {Object.entries(data.terminal_states.by_abstention_reason).map(([reason, count]) => (
                  <tr key={reason} className="border-t border-slate-100 dark:border-slate-800">
                    <td className="py-1.5 text-slate-600 dark:text-slate-300">{reason}</td>
                    <td className="py-1.5 text-right font-mono text-slate-800 dark:text-slate-100">
                      {count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}
    </main>
  );
}
