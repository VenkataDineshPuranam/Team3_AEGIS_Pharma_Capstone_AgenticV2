"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { CaseFile } from "@/components/CaseFile";
import { useRole } from "@/components/RoleProvider";
import { decideRun, getRun, type RunResult } from "@/lib/api";

export default function CasePage() {
  const params = useParams<{ runId: string }>();
  const router = useRouter();
  const { role } = useRole();
  const [run, setRun] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setRun(await getRun(params.runId));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    }
  }, [params.runId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <AppShell title="Case file">
      {error && (
        <div className="mb-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error}
        </div>
      )}
      {!run && !error && <p className="text-sm text-muted">Loading case…</p>}
      {run && (
        <CaseFile
          run={run}
          role={role}
          onDecide={async (d) => {
            const updated = await decideRun(run.run_id, { workflow: run.workflow, ...d });
            setRun(updated);
            if (updated.status !== "pending_approval") {
              router.push(`/runs/${run.run_id}`);
            }
          }}
        />
      )}
    </AppShell>
  );
}
