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
    neutral: "border-slate-200 dark:border-slate-700",
    warn: "border-amber-300 dark:border-amber-700",
    danger: "border-red-300 dark:border-red-700",
    good: "border-emerald-300 dark:border-emerald-700",
  };
  return (
    <div
      className={`rounded-lg border ${toneClasses[tone]} bg-white dark:bg-slate-900 p-4 shadow-sm`}
    >
      <div className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold text-slate-900 dark:text-slate-50">
        {value}
      </div>
      {sub && (
        <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">{sub}</div>
      )}
    </div>
  );
}
