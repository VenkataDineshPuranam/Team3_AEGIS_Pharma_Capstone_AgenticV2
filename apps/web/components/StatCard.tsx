export function StatCard({
  label,
  value,
  sub,
  tone = "neutral",
}: {
  label: string;
  value: string | number;
  sub?: string;
  tone?: "neutral" | "warn" | "danger" | "good";
}) {
  const toneClasses: Record<string, string> = {
    neutral: "border-line",
    warn: "border-amber/50",
    danger: "border-crimson/50",
    good: "border-emerald/40",
  };
  return (
    <div className={`rounded-lg border ${toneClasses[tone]} bg-white p-4`}>
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-navy">{value}</div>
      {sub && <div className="mt-1 text-xs text-muted">{sub}</div>}
    </div>
  );
}
