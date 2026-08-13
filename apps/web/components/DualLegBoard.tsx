"use client";

export function DualLegBoard({
  approvedLegs,
  onDecide,
  busy,
  canPlanning,
  canQuality,
}: {
  approvedLegs: string[];
  onDecide: (action: "approved" | "rejected", leg: "planning" | "quality") => void;
  busy: boolean;
  canPlanning: boolean;
  canQuality: boolean;
}) {
  const legs: { key: "planning" | "quality"; label: string; role: string; can: boolean; note: string }[] = [
    {
      key: "planning",
      label: "Planning leg",
      role: "Supply Chain VP",
      can: canPlanning,
      note: "No escalation role on this leg.",
    },
    {
      key: "quality",
      label: "Quality leg",
      role: "EU Qualified Person",
      can: canQuality,
      note: "Escalates to Chief Quality Officer at T2.",
    },
  ];
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-navy">Partial approval is not approval.</p>
      {legs.map((leg) => {
        const approved = approvedLegs.includes(leg.key);
        return (
          <div key={leg.key} className="flex items-center justify-between gap-3 rounded border border-line bg-white px-3 py-2">
            <div>
              <div className="text-sm font-medium">
                {leg.label} <span className="font-normal text-muted">({leg.role})</span>
              </div>
              <div className="text-xs text-muted">{leg.note}</div>
              {approved && <div className="text-xs text-emerald">Approved</div>}
            </div>
            {!approved && (
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={busy || !leg.can}
                  className="rounded bg-emerald px-3 py-1.5 text-sm text-white disabled:opacity-40"
                  onClick={() => onDecide("approved", leg.key)}
                >
                  Approve
                </button>
                <button
                  type="button"
                  disabled={busy || !leg.can}
                  className="rounded bg-crimson px-3 py-1.5 text-sm text-white disabled:opacity-40"
                  onClick={() => onDecide("rejected", leg.key)}
                >
                  Reject
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
