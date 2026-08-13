"use client";

import Link from "next/link";
import type { QueueEntry, Workflow } from "@/lib/api";
import { SLA } from "@/lib/sla";
import { WORKFLOW_LABEL } from "@/lib/labels";
import { SlaClock } from "./SlaClock";
import { WorkflowBadge } from "./WorkflowBadge";

export function InboxList({
  entries,
  filter,
  onFilter,
  hideFilters = false,
}: {
  entries: QueueEntry[];
  filter: Workflow | "all";
  onFilter: (w: Workflow | "all") => void;
  hideFilters?: boolean;
}) {
  return (
    <div>
      {!hideFilters && (
      <div className="mb-4 flex flex-wrap gap-2 text-sm">
        {(["all", "batch_review", "pv_intake", "supply_planning"] as const).map((w) => (
          <button
            key={w}
            type="button"
            onClick={() => onFilter(w)}
            className={`rounded-full border px-3 py-1 ${
              filter === w ? "border-navy bg-navy text-white" : "border-line text-muted"
            }`}
          >
            {w === "all" ? "All" : WORKFLOW_LABEL[w]}
          </button>
        ))}
      </div>
      )}
      {entries.length === 0 && (
        <p className="text-sm text-muted">Nothing pending for this role. Submit a run from a workspace.</p>
      )}
      <ul className="space-y-2">
        {entries.map((e) => (
          <li key={e.run_id}>
            <Link
              href={`/inbox/${e.run_id}`}
              className="flex items-center justify-between gap-3 rounded border border-line bg-white px-4 py-3 hover:border-navy/30"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <WorkflowBadge workflow={e.workflow} />
                  <span className="font-mono text-sm">{e.subject_id}</span>
                </div>
                <p className="mt-1 truncate text-sm text-muted">{e.draft_summary ?? "Awaiting review"}</p>
              </div>
              <SlaClock
                deadline={e.hitl_deadline}
                tier={e.hitl_tier}
                clock={SLA[e.workflow].clock}
              />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
