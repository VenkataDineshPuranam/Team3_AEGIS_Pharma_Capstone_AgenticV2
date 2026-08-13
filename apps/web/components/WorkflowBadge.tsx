import type { Workflow } from "@/lib/api";

const LABELS: Record<Workflow, string> = {
  batch_review: "Batch Review",
  pv_intake: "PV Intake",
  supply_planning: "Supply Planning",
};

const COLORS: Record<Workflow, string> = {
  batch_review: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  pv_intake: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300",
  supply_planning:
    "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
};

export function WorkflowBadge({ workflow }: { workflow: Workflow }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${COLORS[workflow]}`}
    >
      {LABELS[workflow]}
    </span>
  );
}
