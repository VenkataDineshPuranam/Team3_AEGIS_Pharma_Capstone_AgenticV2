"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AdminShell } from "@/components/AdminShell";
import { listRuns, type RunResult } from "@/lib/api";

export default function RunsPage() {
  const [runs, setRuns] = useState<RunResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    listRuns()
      .then(setRuns)
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, []);
  return (
    <AdminShell title="Run inspector">
      {error && <p className="text-sm text-crimson">{error}</p>}
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-muted">
            <th className="py-2">Run</th>
            <th>Workflow</th>
            <th>Status</th>
            <th>LLM</th>
            <th>Tokens</th>
            <th>Critic</th>
            <th>Policy</th>
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
              <td>{r.workflow}</td>
              <td>{r.status}</td>
              <td>{r.llm_calls ?? "—"}</td>
              <td className="font-mono">
                {(r.tokens_in ?? 0) + (r.tokens_out ?? 0) || "—"}
              </td>
              <td className="text-xs">{r.critic_reason_codes?.join(", ") || "—"}</td>
              <td className="font-mono text-xs">{r.policy_contract_version ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </AdminShell>
  );
}
