import { statusLabel } from "@/lib/labels";

const TONE: Record<string, string> = {
  pending_approval: "bg-amber/15 text-amber border-amber/30",
  completed: "bg-emerald/10 text-emerald border-emerald/30",
  abstained: "bg-slate-100 text-slate-700 border-slate-200",
  blocked: "bg-crimson/10 text-crimson border-crimson/30",
  refused: "bg-crimson/10 text-crimson border-crimson/30",
  timed_out: "bg-amber/10 text-amber border-amber/40",
};

export function StatusChip({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${TONE[status] ?? "bg-slate-100 text-slate-600"}`}
    >
      {statusLabel(status)}
    </span>
  );
}
