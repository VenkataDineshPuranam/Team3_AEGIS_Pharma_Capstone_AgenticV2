"use client";

import { useState } from "react";
import Link from "next/link";
import { submitRun, type RunResult, type Workflow } from "@/lib/api";
import { DEFAULT_REQUESTER, SUBJECT_OPTIONS, WORKFLOW_LABEL } from "@/lib/labels";
import { WorkflowBadge } from "./WorkflowBadge";
import { StatusChip } from "./StatusChip";

export function SubmitForm({
  defaultWorkflow = "batch_review",
  lockWorkflow = false,
}: {
  defaultWorkflow?: Workflow;
  lockWorkflow?: boolean;
}) {
  const [workflow, setWorkflow] = useState<Workflow>(defaultWorkflow);
  const [subjectId, setSubjectId] = useState(SUBJECT_OPTIONS[defaultWorkflow][0]);
  const [requesterRole, setRequesterRole] = useState(DEFAULT_REQUESTER[defaultWorkflow]);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function onWorkflowChange(w: Workflow) {
    setWorkflow(w);
    setSubjectId(SUBJECT_OPTIONS[w][0]);
    setRequesterRole(DEFAULT_REQUESTER[w]);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await submitRun({ workflow, subject_id: subjectId, requester_role: requesterRole }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-xl">
      <form onSubmit={onSubmit} className="space-y-4 rounded border border-line bg-white p-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Workflow</label>
          <select
            className="w-full rounded border border-line px-3 py-2 text-sm"
            value={workflow}
            disabled={lockWorkflow}
            onChange={(e) => onWorkflowChange(e.target.value as Workflow)}
          >
            {(Object.keys(WORKFLOW_LABEL) as Workflow[]).map((w) => (
              <option key={w} value={w}>
                {WORKFLOW_LABEL[w]}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Subject</label>
          <select
            className="w-full rounded border border-line px-3 py-2 font-mono text-sm"
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
          <label className="mb-1 block text-sm font-medium">Requester role</label>
          <input
            className="w-full rounded border border-line px-3 py-2 text-sm"
            value={requesterRole}
            onChange={(e) => setRequesterRole(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-navy px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "Running…" : "Submit run"}
        </button>
      </form>
      {error && (
        <div className="mt-4 rounded border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm text-crimson">
          {error}
        </div>
      )}
      {result && (
        <div className="mt-4 space-y-2 rounded border border-line bg-white p-4">
          <div className="flex items-center gap-2">
            <WorkflowBadge workflow={result.workflow} />
            <StatusChip status={result.status} />
            <span className="font-mono text-xs text-muted">{result.run_id}</span>
          </div>
          {result.abstention_reason && (
            <p className="text-sm">
              Abstention: {result.abstention_reason}
              {result.abstention_reason === "hitl_timeout" ? " — No decision was made; resubmit." : ""}
            </p>
          )}
          {result.status === "pending_approval" && (
            <Link className="text-sm text-batch hover:underline" href={`/inbox/${result.run_id}`}>
              Open case file →
            </Link>
          )}
          {result.status !== "pending_approval" && (
            <Link className="text-sm text-batch hover:underline" href={`/runs/${result.run_id}`}>
              View run →
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
