"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { CaseFile } from "@/components/CaseFile";
import { useRole } from "@/components/RoleProvider";
import { getRun, type RunResult } from "@/lib/api";

export default function RunDetailPage() {
  const params = useParams<{ runId: string }>();
  const { role } = useRole();
  const [run, setRun] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRun(params.runId)
      .then(setRun)
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, [params.runId]);

  return (
    <AppShell title="Run record">
      {error && (
        <div className="mb-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error}
        </div>
      )}
      {run && (
        <CaseFile
          run={run}
          role={role}
          readOnly={run.status !== "pending_approval"}
          onDecide={async () => undefined}
        />
      )}
    </AppShell>
  );
}
