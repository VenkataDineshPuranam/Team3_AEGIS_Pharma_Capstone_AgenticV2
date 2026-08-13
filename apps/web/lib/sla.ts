export const SLA = {
  batch_review: { clock: "Business hours", t1: 8, t2: 16, t3: 24, unit: "bh" },
  pv_intake: { clock: "Wall clock", t1: 4, t2: 8, t3: 24, unit: "h" },
  supply_planning: { clock: "Business hours", t1: 8, t2: 16, t3: 24, unit: "bh" },
} as const;

export type SlaWorkflow = keyof typeof SLA;

export function hoursUntil(iso: string | null | undefined): number | null {
  if (!iso) return null;
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return null;
  return (t - Date.now()) / 3600000;
}

export function formatCountdown(iso: string | null | undefined): string {
  const h = hoursUntil(iso);
  if (h === null) return "—";
  if (h <= 0) return "Past deadline";
  if (h < 1) return `${Math.max(1, Math.round(h * 60))} min`;
  return `${h.toFixed(1)} h`;
}
