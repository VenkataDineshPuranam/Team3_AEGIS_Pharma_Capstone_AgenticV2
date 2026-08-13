"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/AdminShell";
import { getGuardrails, type GuardrailEvent } from "@/lib/api";

export default function GuardrailsPage() {
  const [rows, setRows] = useState<GuardrailEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    getGuardrails()
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, []);
  return (
    <AdminShell title="Prohibited-action log">
      <p className="mb-4 text-sm text-muted">
        Blocked drafts are not stored. This log shows reason class and a SHA-256 of the discarded text.
      </p>
      {error && <p className="text-sm text-crimson">{error}</p>}
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-muted">
            <th className="py-2">Run</th>
            <th>Workflow</th>
            <th>Matched terms</th>
            <th>Draft hash</th>
            <th>When</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={`${r.run_id}-${r.recorded_at}`} className="border-t border-line">
              <td className="py-2 font-mono">{r.run_id}</td>
              <td>{r.workflow ?? "—"}</td>
              <td>{r.matched_terms.join(", ") || r.abstention_reason || "—"}</td>
              <td className="font-mono text-xs">{r.draft_sha256 ?? "—"}</td>
              <td className="text-xs text-muted">{r.recorded_at ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <p className="mt-4 text-sm text-muted">No blocked events.</p>}
    </AdminShell>
  );
}
