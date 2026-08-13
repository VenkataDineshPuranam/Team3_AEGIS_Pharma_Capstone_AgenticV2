export type Workflow = "batch_review" | "pv_intake" | "supply_planning";

export const WORKFLOW_LABEL: Record<Workflow, string> = {
  batch_review: "Batch Review",
  pv_intake: "PV Intake",
  supply_planning: "Supply Planning",
};

export const WORKFLOW_HREF: Record<Workflow, string> = {
  batch_review: "/workflows/batch-review",
  pv_intake: "/workflows/pv-intake",
  supply_planning: "/workflows/supply-planning",
};

export const PROHIBITIONS: Record<Workflow, string[]> = {
  batch_review: ["release", "reject (batch)", "reprocess", "relabel", "recall"],
  pv_intake: ["causality", "seriousness", "expectedness", "reportability", "signal confirmation"],
  supply_planning: ["allocate", "reserve", "ship", "change inventory status", "recall"],
};

export const SUBJECT_OPTIONS: Record<Workflow, string[]> = {
  batch_review: ["B-001", "B-002", "B-003"],
  pv_intake: ["PV-001", "PV-002"],
  supply_planning: ["P-100", "P-200"],
};

export const DEFAULT_REQUESTER: Record<Workflow, string> = {
  batch_review: "EU Qualified Person",
  pv_intake: "Global Head of Pharmacovigilance",
  supply_planning: "Supply Chain VP",
};

export const FINDING_LABELS: Record<string, string> = {
  genealogy: "Genealogy",
  lab_results: "Lab results",
  environmental_monitoring: "Environmental monitoring",
  deviations: "Deviations",
  capa: "CAPA",
  change_control: "Change control",
  validation_state: "Validation state",
  supplier_evidence: "Supplier evidence",
  release_packet_completeness: "Release packet completeness",
};

export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    pending_approval: "Pending approval",
    completed: "Completed",
    abstained: "Abstained",
    blocked: "Blocked",
    refused: "Refused",
    timed_out: "Timed out",
  };
  return map[status] ?? status;
}
