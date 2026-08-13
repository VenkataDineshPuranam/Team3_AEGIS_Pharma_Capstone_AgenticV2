import type { ReconciliationFinding } from "@/lib/api";
import { FINDING_LABELS } from "@/lib/labels";

const STATUS_COPY = {
  complete: { label: "Complete", className: "text-emerald" },
  gap: { label: "Gap", className: "text-amber" },
  conflict: { label: "Conflict — both sources shown, not resolved", className: "text-crimson" },
};

export function FindingGrid({
  findings,
  onCite,
}: {
  findings: ReconciliationFinding[];
  onCite?: (ids: string[]) => void;
}) {
  if (!findings.length) return <p className="text-sm text-muted">No reconciliation findings.</p>;
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {findings.map((f) => {
        const s = STATUS_COPY[f.status];
        return (
          <button
            type="button"
            key={f.category}
            className="rounded border border-line bg-white p-3 text-left"
            onClick={() => onCite?.(f.evidence_ids)}
          >
            <div className="text-sm font-medium text-navy">
              {FINDING_LABELS[f.category] ?? f.category}
            </div>
            <div className={`mt-1 text-xs font-medium ${s.className}`}>{s.label}</div>
            {f.gap_description && <p className="mt-1 text-xs text-muted">{f.gap_description}</p>}
          </button>
        );
      })}
    </div>
  );
}
