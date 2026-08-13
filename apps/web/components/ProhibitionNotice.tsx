import type { Workflow } from "@/lib/api";
import { PROHIBITIONS } from "@/lib/labels";

export function ProhibitionNotice({ workflow }: { workflow: Workflow }) {
  return (
    <aside className="rounded border border-line bg-white p-3 text-xs text-muted">
      <div className="font-semibold uppercase tracking-wide text-navy">Decision support</div>
      <p className="mt-1">
        Approve means you accept this evidence pack for human use. It does not certify, allocate, or
        determine safety.
      </p>
      <p className="mt-2 font-medium text-ink">This workflow must never:</p>
      <ul className="mt-1 list-disc pl-4">
        {PROHIBITIONS[workflow].map((p) => (
          <li key={p}>{p}</li>
        ))}
      </ul>
    </aside>
  );
}
