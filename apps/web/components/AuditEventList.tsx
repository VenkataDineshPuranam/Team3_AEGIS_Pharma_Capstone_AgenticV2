import type { AuditEvent } from "@/lib/api";

export function AuditEventList({ events }: { events: AuditEvent[] }) {
  if (!events.length) return <p className="text-sm text-muted">No audit events yet.</p>;
  return (
    <ol className="space-y-2">
      {events.map((e, i) => (
        <li key={i} className="rounded border border-line bg-white px-3 py-2 text-sm">
          <div className="font-medium text-navy">{String(e.kind)}</div>
          <div className="font-mono text-xs text-muted">
            {String(e.recorded_at ?? e.action ?? "")}
            {e.role ? ` · ${String(e.role)}` : ""}
            {e.action ? ` · ${String(e.action)}` : ""}
          </div>
          {e.justification ? (
            <p className="mt-1 text-ink">{String(e.justification)}</p>
          ) : null}
          {e.message ? <p className="mt-1 text-amber">{String(e.message)}</p> : null}
        </li>
      ))}
    </ol>
  );
}
