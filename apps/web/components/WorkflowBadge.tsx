import type { Workflow } from "@/lib/api";
import { WORKFLOW_LABEL } from "@/lib/labels";

const COLORS: Record<Workflow, string> = {
  batch_review: "bg-blue-100 text-batch",
  pv_intake: "bg-violet-100 text-pv",
  supply_planning: "bg-amber-100 text-supply",
};

export function WorkflowBadge({ workflow }: { workflow: Workflow }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${COLORS[workflow]}`}>
      {WORKFLOW_LABEL[workflow]}
    </span>
  );
}
