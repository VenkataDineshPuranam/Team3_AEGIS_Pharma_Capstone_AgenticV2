"use client";

import { useState } from "react";
import type { QueueEntry } from "@/lib/api";
import { WorkflowBadge } from "./WorkflowBadge";
import { DecisionButtons } from "./DecisionButtons";

export function PendingItemCard({
  entry,
  onDecide,
}: {
  entry: QueueEntry;
  onDecide: (
    runId: string,
    decision:
      | { action: "approved" | "rejected" | "veto" }
      | { action: "approved" | "rejected"; leg: "planning" | "quality" },
  ) => Promise<void>;
}) {
  const [expanded, setExpanded] = useState(false);
  const [busy, setBusy] = useState(false);

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
      <button
        className="w-full text-left px-4 py-3 flex items-center justify-between gap-3 hover:bg-slate-50 dark:hover:bg-slate-800/60"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-center gap-3 min-w-0">
          <WorkflowBadge workflow={entry.workflow} />
          <span className="font-mono text-sm text-slate-700 dark:text-slate-300">
            {entry.subject_id}
          </span>
          <span className="text-xs text-slate-400 truncate">
            requested by {entry.requester_role}
          </span>
        </div>
        <span className="text-slate-400 text-sm">{expanded ? "▲" : "▼"}</span>
      </button>

      {expanded && (
        <div className="border-t border-slate-100 dark:border-slate-800 px-4 py-4 space-y-4">
          <div>
            <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">
              Draft summary
            </div>
            <p className="text-sm text-slate-800 dark:text-slate-100">
              {entry.draft_summary || "(no draft -- refused/abstained before synthesis)"}
            </p>
          </div>

          {entry.draft_claims.length > 0 && (
            <div>
              <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">
                Claims &amp; citations
              </div>
              <ul className="space-y-1">
                {entry.draft_claims.map((c, i) => (
                  <li key={i} className="text-sm text-slate-700 dark:text-slate-300">
                    {c.text}{" "}
                    <span className="text-xs text-slate-400">
                      [{c.cites.join(", ") || "no citation"}]
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">
              Approver role(s)
            </div>
            <p className="text-sm text-slate-700 dark:text-slate-300">
              {entry.approver_roles.join(", ")}
            </p>
          </div>

          <DecisionButtons
            entry={entry}
            busy={busy}
            onDecide={async (decision) => {
              setBusy(true);
              try {
                await onDecide(entry.run_id, decision);
              } finally {
                setBusy(false);
              }
            }}
          />
        </div>
      )}
    </div>
  );
}
