"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/AdminShell";
import { getGovernance, type GovernanceResponse } from "@/lib/api";

export default function GovernancePage() {
  const [data, setData] = useState<GovernanceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    getGovernance()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, []);
  return (
    <AdminShell title="Governance">
      {error && <p className="text-sm text-crimson">{error}</p>}
      {data && (
        <div className="space-y-4 text-sm">
          <div className="rounded border border-line bg-white p-4">
            <div className="text-xs uppercase text-muted">Policy engine</div>
            <p className={data.policy_engine_ok ? "text-emerald" : "text-crimson"}>
              {data.policy_engine_ok ? "Reachable" : "Unreachable — fail closed"}
            </p>
            <p className="font-mono">version {data.policy_contract_version ?? "—"}</p>
            <p className="text-muted">{data.detail}</p>
          </div>
          <div className="rounded border border-line bg-white p-4">
            <div className="text-xs uppercase text-muted">HITL ladder (read-only)</div>
            <pre className="mt-2 overflow-auto text-xs">{JSON.stringify(data.hitl_ladder, null, 2)}</pre>
            <p className="mt-2 text-muted">{data.note}</p>
          </div>
        </div>
      )}
    </AdminShell>
  );
}
