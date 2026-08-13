import { formatCountdown } from "@/lib/sla";

export function SlaClock({
  deadline,
  tier,
  clock,
}: {
  deadline?: string | null;
  tier?: string | null;
  clock?: string;
}) {
  const past = deadline ? new Date(deadline).getTime() < Date.now() : false;
  return (
    <div className={`text-sm ${past ? "text-crimson" : "text-ink"}`}>
      <span className="font-mono text-xs uppercase tracking-wide text-muted">{tier ?? "T0"}</span>
      <div className="font-semibold">{formatCountdown(deadline)}</div>
      {clock && <div className="text-xs text-muted">{clock}</div>}
    </div>
  );
}
