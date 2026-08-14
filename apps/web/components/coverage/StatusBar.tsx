import { COVERAGE_STATUS_BAR_CLASS, COVERAGE_STATUS_ORDER } from "@/lib/coverage-format";
import type { CoverageStatus } from "@/lib/api";

/**
 * Stacked composition bar over the 4 coverage statuses -- the dimension matrix's core
 * visual. Order is fixed (COVERED, PARTIAL, NOT_COVERED, OUT_OF_SCOPE) so every bar in
 * the matrix reads left-to-right the same way, making the column of bars comparable at a
 * glance rather than each one needing to be read independently.
 */
export function StatusBar({
  counts,
  total,
  height = "h-2.5",
}: {
  counts: Partial<Record<CoverageStatus, number>>;
  total: number;
  height?: string;
}) {
  if (total === 0) return null;
  return (
    <div className={`flex ${height} w-full overflow-hidden rounded-[var(--radius-full)] bg-[var(--surface-sunken)]`}>
      {COVERAGE_STATUS_ORDER.map((status) => {
        const value = counts[status] ?? 0;
        if (value === 0) return null;
        return (
          <div
            key={status}
            className={COVERAGE_STATUS_BAR_CLASS[status]}
            style={{ width: `${(value / total) * 100}%` }}
            title={`${status}: ${value} of ${total}`}
          />
        );
      })}
    </div>
  );
}
