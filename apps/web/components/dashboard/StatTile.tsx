import Link from "next/link";
import type { ReactNode } from "react";
import { cn } from "@/lib/cn";
import { NotAvailable } from "@/components/ui/Card";

/**
 * A single metric.
 *
 * `value` is `string | number | null`, and null renders "Not available" rather than a
 * zero or a dash. This is Phase 5's rule made structural: a tile physically cannot
 * display a fabricated number for a metric the backend did not return, because there is
 * no code path from null to a digit.
 */
export function StatTile({
  label,
  value,
  sub,
  tone = "neutral",
  href,
  unavailableReason,
}: {
  label: string;
  value: string | number | null;
  sub?: ReactNode;
  tone?: "neutral" | "ok" | "pending" | "blocked" | "info";
  href?: string;
  /** Why the value is missing -- surfaced on hover so "Not available" isn't a dead end. */
  unavailableReason?: string;
}) {
  const accent = {
    neutral: "text-[var(--text-primary)]",
    ok: "text-[var(--status-ok-fg)]",
    pending: "text-[var(--status-pending-fg)]",
    blocked: "text-[var(--status-blocked-fg)]",
    info: "text-[var(--status-info-fg)]",
  }[tone];

  const body = (
    <>
      <p className="text-[11px] font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
        {label}
      </p>
      <p className={cn("mt-1.5 text-2xl font-semibold tabular-nums tracking-tight", accent)}>
        {value === null ? (
          <span className="text-base font-normal">
            <NotAvailable reason={unavailableReason} />
          </span>
        ) : (
          value
        )}
      </p>
      {sub && <div className="mt-1 text-xs text-[var(--text-tertiary)]">{sub}</div>}
    </>
  );

  const className = cn(
    "block rounded-[var(--radius-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] p-4 shadow-[var(--shadow-sm)]",
    href && "transition-colors hover:border-[var(--border-strong)] hover:bg-[var(--surface-sunken)]",
  );

  return href ? (
    <Link href={href} className={className}>
      {body}
    </Link>
  ) : (
    <div className={className}>{body}</div>
  );
}

/**
 * Proportional bar for a distribution (terminal states, evidence statuses).
 *
 * Deliberately a stacked bar and a legend rather than a pie or a charting library: the
 * question these answer is "what share of runs ended each way", which a single bar shows
 * more precisely than a pie and without adding a dependency (Phase 27).
 */
export function DistributionBar({
  segments,
  total,
}: {
  segments: { label: string; value: number; className: string }[];
  total: number;
}) {
  if (total === 0) return null;
  return (
    <div className="flex h-2 w-full overflow-hidden rounded-[var(--radius-full)] bg-[var(--surface-sunken)]">
      {segments
        .filter((s) => s.value > 0)
        .map((s) => (
          <div
            key={s.label}
            className={s.className}
            style={{ width: `${(s.value / total) * 100}%` }}
            title={`${s.label}: ${s.value} of ${total}`}
          />
        ))}
    </div>
  );
}
