"use client";

import { useState } from "react";
import type { RunResult } from "@/lib/api";
import { DualLegBoard } from "./DualLegBoard";
import { JustificationField } from "./JustificationField";
import type { RoleDef } from "@/lib/roles";
import { canApproveWorkflow } from "@/lib/roles";

export function DecisionRail({
  run,
  role,
  busy,
  onDecide,
}: {
  run: RunResult;
  role: RoleDef;
  busy: boolean;
  onDecide: (
    decision:
      | { action: "approved" | "rejected" | "veto"; justification: string }
      | { action: "approved" | "rejected"; leg: "planning" | "quality"; justification: string },
  ) => Promise<void>;
}) {
  const [justification, setJustification] = useState("");
  if (run.status !== "pending_approval") {
    if (run.status === "timed_out" || run.abstention_reason === "hitl_timeout") {
      return (
        <p className="rounded border border-amber/40 bg-amber/10 p-3 text-sm text-amber">
          No decision was made; resubmit.
        </p>
      );
    }
    return null;
  }

  const can = canApproveWorkflow(role, run.workflow) || (role.canVetoPv && run.workflow === "pv_intake");
  if (role.requesterOnly) {
    return (
      <p className="text-sm text-muted">
        Manufacturing VP is never a Batch approver. This role may request work, not sign the pack.
      </p>
    );
  }

  async function go(
    decision:
      | { action: "approved" | "rejected" | "veto" }
      | { action: "approved" | "rejected"; leg: "planning" | "quality" },
  ) {
    if (justification.trim().length < 8) return;
    await onDecide({ ...decision, justification: justification.trim() } as Parameters<typeof onDecide>[0]);
  }

  return (
    <div className="sticky bottom-0 space-y-3 rounded border border-navy/20 bg-white p-4 shadow-sm">
      <JustificationField value={justification} onChange={setJustification} disabled={busy || !can} />
      {run.workflow === "supply_planning" ? (
        <DualLegBoard
          approvedLegs={run.approved_legs}
          busy={busy || justification.trim().length < 8}
          canPlanning={role.supplyLeg === "planning"}
          canQuality={role.supplyLeg === "quality"}
          onDecide={(action, leg) => go({ action, leg })}
        />
      ) : (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy || !canApproveWorkflow(role, run.workflow) || justification.trim().length < 8}
            className="rounded bg-emerald px-3 py-1.5 text-sm text-white disabled:opacity-40"
            onClick={() => go({ action: "approved" })}
          >
            Accept evidence pack
          </button>
          <button
            type="button"
            disabled={busy || !canApproveWorkflow(role, run.workflow) || justification.trim().length < 8}
            className="rounded bg-crimson px-3 py-1.5 text-sm text-white disabled:opacity-40"
            onClick={() => go({ action: "rejected" })}
          >
            Reject pack
          </button>
          {run.workflow === "pv_intake" && (
            <button
              type="button"
              disabled={busy || !role.canVetoPv || justification.trim().length < 8}
              className="rounded bg-navy px-3 py-1.5 text-sm text-white disabled:opacity-40"
              title="Advisory veto — forces rejected, never overridden"
              onClick={() => go({ action: "veto" })}
            >
              Veto (Patient Safety Rep)
            </button>
          )}
        </div>
      )}
    </div>
  );
}
