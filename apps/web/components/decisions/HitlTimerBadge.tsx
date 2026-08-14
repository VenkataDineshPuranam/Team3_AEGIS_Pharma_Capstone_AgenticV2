"use client";

import { Badge } from "@/components/ui/Badge";
import { HITL_TIER_NEXT_STEP, HITL_TIER_TONE } from "@/lib/format";
import type { HitlTimerInfo } from "@/lib/api";

/** Formats hours (a float) as "3h 42m" / "18m" — same granularity as lib/format.ts's
 * formatAge, but from a known hour count rather than re-deriving from a timestamp. */
function formatHours(hours: number): string {
  const totalMinutes = Math.max(0, Math.round(hours * 60));
  const h = Math.floor(totalMinutes / 60);
  const m = totalMinutes % 60;
  if (h === 0) return `${m}m`;
  return `${h}h ${m}m`;
}

/**
 * The wait-severity badge shown on every pending decision — Decision Queue rows and the
 * Decision Detail page. Backed by services/integration/hitl_timer.py, recomputed fresh on
 * every poll (the Decision Queue already polls every 10s), so this is live without any
 * websocket or notification channel.
 */
export function HitlTimerBadge({ timer, size = "sm" }: { timer: HitlTimerInfo; size?: "xs" | "sm" }) {
  const tone = HITL_TIER_TONE[timer.tier] ?? "neutral";
  const hint = HITL_TIER_NEXT_STEP[timer.tier] ?? "";
  return (
    <Badge tone={tone} size={size} title={hint}>
      Severity {timer.severity} · {timer.label} · {formatHours(timer.hours_elapsed)} waiting
    </Badge>
  );
}
