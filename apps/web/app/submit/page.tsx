"use client";

import { useState } from "react";
import Link from "next/link";
import { submitRun, type RunResult, type Workflow } from "@/lib/api";
import { WorkflowBadge } from "@/components/WorkflowBadge";

// hitl_control_model.md SS2 -- named, accountable primary approver per workflow.
const DEFAULT_ROLE: Record<Workflow, string> = {
  batch_review: "EU Qualified Person",
  pv_intake: "Global Head of Pharmacovigilance",
  supply_planning: "Supply Chain VP",
};

// tests/fixtures/synthetic/* -- the only subject ids the backend can actually resolve.
const SUBJECT_OPTIONS: Record<Workflow, string[]> = {
  batch_review: ["B-001", "B-002", "B-003"],
  pv_intake: ["PV-001", "PV-002"],
  supply_planning: ["P-100", "P-200"],
};

export default function SubmitPage() {
  const [workflow, setWorkflow] = useState<Workflow>("batch_review");
  const [subjectId, setSubjectId] = useState(SUBJECT_OPTIONS.batch_review[0]);
  const [requesterRole, setRequesterRole] = useState(DEFAULT_ROLE.batch_review);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function onWorkflowChange(w: Workflow) {
    setWorkflow(w);
    setSubjectId(SUBJECT_OPTIONS[w][0]);
    setRequesterRole(DEFAULT_ROLE[w]);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const r = await submitRun({ workflow, subject_id: subjectId, requester_role: requesterRole });
      setResult(r);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-xl px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
          Submit a run
        </h1>
        <Link className="text-sm text-blue-600 hover:underline" href="/">
          ← Approver Dashboard
        </Link>
      </header>

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Workflow
          </label>
          <select
            className="w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
            value={workflow}
            onChange={(e) => onWorkflowChange(e.target.value as Workflow)}
          >
            <option value="batch_review">Batch Review</option>
            <option value="pv_intake">PV Intake</option>
            <option value="supply_planning">Supply Planning</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Subject (batch / case / product id)
          </label>
          <select
            className="w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm font-mono"
            value={subjectId}
            onChange={(e) => setSubjectId(e.target.value)}
          >
            {SUBJECT_OPTIONS[workflow].map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Requester role
          </label>
          <input
            className="w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
            value={requesterRole}
            onChange={(e) => setRequesterRole(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={busy}
          className="rounded-md bg-slate-900 dark:bg-slate-50 text-white dark:text-slate-900 px-4 py-2 text-sm font-medium disabled:opacity-50"
        >
          {busy ? "Running…" : "Submit"}
        </button>
      </form>

      {error && (
        <div className="mt-6 rounded-md border border-red-300 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 space-y-2">
          <div className="flex items-center gap-2">
            <WorkflowBadge workflow={result.workflow} />
            <span className="text-sm font-mono text-slate-500">{result.run_id}</span>
          </div>
          <div className="text-sm">
            Status: <span className="font-semibold">{result.status}</span>
            {result.abstention_reason && ` (${result.abstention_reason})`}
          </div>
          {result.draft_summary && (
            <p className="text-sm text-slate-700 dark:text-slate-300">
              {result.draft_summary}
            </p>
          )}
          {result.status === "pending_approval" && (
            <p className="text-sm text-blue-600">
              <Link href="/" className="hover:underline">
                → Review in the Approver Dashboard
              </Link>
            </p>
          )}
        </div>
      )}
    </main>
  );
}
