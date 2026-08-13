"use client";

import type { QueueEntry } from "@/lib/api";

type Decision =
  | { action: "approved" | "rejected" | "veto" }
  | { action: "approved" | "rejected"; leg: "planning" | "quality" };

export function DecisionButtons({
  entry,
  onDecide,
  busy,
}: {
  entry: QueueEntry;
  onDecide: (decision: Decision) => void;
  busy: boolean;
}) {
  const btn =
    "rounded-md px-3 py-1.5 text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors";

  if (entry.workflow === "supply_planning") {
    // Dual approval: Supply Chain VP (planning leg) + EU QP (quality leg), both required.
    // hitl_control_model.md SS2 -- one leg approving is NOT approval.
    const legs: { key: "planning" | "quality"; label: string; role: string }[] = [
      { key: "planning", label: "Planning leg", role: "Supply Chain VP" },
      { key: "quality", label: "Quality leg", role: "EU Qualified Person" },
    ];
    return (
      <div className="flex flex-col gap-2">
        {legs.map((leg) => {
          const approved = entry.approved_legs.includes(leg.key);
          return (
            <div
              key={leg.key}
              className="flex items-center justify-between gap-3 rounded-md border border-slate-200 dark:border-slate-700 px-3 py-2"
            >
              <div>
                <div className="text-sm font-medium text-slate-800 dark:text-slate-100">
                  {leg.label}{" "}
                  <span className="text-slate-400 font-normal">({leg.role})</span>
                </div>
                {approved && (
                  <div className="text-xs text-emerald-600 dark:text-emerald-400">
                    Approved
                  </div>
                )}
              </div>
              {!approved && (
                <div className="flex gap-2">
                  <button
                    className={`${btn} bg-emerald-600 text-white hover:bg-emerald-700`}
                    disabled={busy}
                    onClick={() => onDecide({ action: "approved", leg: leg.key })}
                  >
                    Approve
                  </button>
                  <button
                    className={`${btn} bg-red-600 text-white hover:bg-red-700`}
                    disabled={busy}
                    onClick={() => onDecide({ action: "rejected", leg: leg.key })}
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          );
        })}
        <p className="text-xs text-slate-400">
          Both legs must approve independently. One leg approving does not complete the run.
        </p>
      </div>
    );
  }

  return (
    <div className="flex gap-2">
      <button
        className={`${btn} bg-emerald-600 text-white hover:bg-emerald-700`}
        disabled={busy}
        onClick={() => onDecide({ action: "approved" })}
      >
        Approve
      </button>
      <button
        className={`${btn} bg-red-600 text-white hover:bg-red-700`}
        disabled={busy}
        onClick={() => onDecide({ action: "rejected" })}
      >
        Reject
      </button>
      {entry.workflow === "pv_intake" && (
        <button
          className={`${btn} bg-slate-800 text-white hover:bg-slate-900`}
          disabled={busy}
          title="Patient Safety Representative advisory veto -- forces rejected, never overridden"
          onClick={() => onDecide({ action: "veto" })}
        >
          Veto (Patient Safety Rep)
        </button>
      )}
    </div>
  );
}
