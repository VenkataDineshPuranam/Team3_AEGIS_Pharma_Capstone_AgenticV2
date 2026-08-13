"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AdminShell } from "@/components/AdminShell";
import { getRun, type RunResult } from "@/lib/api";

export default function RunInspectorDetail() {
  const params = useParams<{ runId: string }>();
  const [run, setRun] = useState<RunResult | null>(null);
  useEffect(() => {
    getRun(params.runId).then(setRun).catch(() => setRun(null));
  }, [params.runId]);
  return (
    <AdminShell title="Run inspector">
      {!run && <p className="text-sm text-muted">Loading…</p>}
      {run && (
        <dl className="grid grid-cols-2 gap-3 text-sm">
          {Object.entries({
            run_id: run.run_id,
            workflow: run.workflow,
            status: run.status,
            terminal: run.terminal_state,
            abstention: run.abstention_reason,
            llm_calls: run.llm_calls,
            tool_calls: run.tool_calls,
            tokens_in: run.tokens_in,
            tokens_out: run.tokens_out,
            critic: run.critic_reason_codes?.join(", "),
            policy: run.policy_contract_version,
            trace_id: run.trace_id,
            guard: run.guard_verdict,
          }).map(([k, v]) => (
            <div key={k} className="rounded border border-line bg-white p-3">
              <dt className="text-xs uppercase text-muted">{k}</dt>
              <dd className="font-mono">{String(v ?? "—")}</dd>
            </div>
          ))}
        </dl>
      )}
    </AdminShell>
  );
}
