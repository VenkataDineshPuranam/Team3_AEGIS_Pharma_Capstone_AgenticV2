import type { BadgeTone } from "@/components/ui/Badge";
import type { CoverageStatus } from "@/lib/api";

/**
 * Vocabulary for the Evaluation & Security Coverage dashboard.
 *
 * Four statuses, and they are deliberately NOT collapsed into a binary "pass/fail" the
 * way a naive coverage percentage would: OUT_OF_SCOPE and NOT_COVERED look similar in a
 * spreadsheet but mean opposite things for what to do next -- one is "this was never
 * going to be built by this system" (a scope statement), the other is "this could be
 * addressed and currently isn't" (a real gap). Merging them would hide exactly the
 * information this dashboard exists to surface.
 */
export const COVERAGE_STATUS_LABELS: Record<CoverageStatus, string> = {
  COVERED: "Covered",
  PARTIAL: "Partial",
  OUT_OF_SCOPE: "Out of scope",
  NOT_COVERED: "Not covered",
};

export const COVERAGE_STATUS_TONE: Record<CoverageStatus, BadgeTone> = {
  COVERED: "ok",
  PARTIAL: "pending",
  OUT_OF_SCOPE: "neutral",
  NOT_COVERED: "blocked",
};

export const COVERAGE_STATUS_BAR_CLASS: Record<CoverageStatus, string> = {
  COVERED: "bg-[var(--status-ok-fg)]",
  PARTIAL: "bg-[var(--status-pending-fg)]",
  OUT_OF_SCOPE: "bg-[var(--text-tertiary)]",
  NOT_COVERED: "bg-[var(--status-blocked-fg)]",
};

export const COVERAGE_STATUS_MEANING: Record<CoverageStatus, string> = {
  COVERED: "A genuine, working control, test, or document addresses this exact scenario.",
  PARTIAL: "A related structural safeguard exists but does not fully address the specifics.",
  OUT_OF_SCOPE: "V3 does not build this domain at all -- it was never going to be addressed by this system.",
  NOT_COVERED: "Within V3's real scope, but nothing addresses it yet -- a genuine gap.",
};

export const COVERAGE_STATUS_ORDER: CoverageStatus[] = [
  "COVERED",
  "PARTIAL",
  "NOT_COVERED",
  "OUT_OF_SCOPE",
];

export function humanizeCategory(category: string): string {
  return category
    .split("_")
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}
