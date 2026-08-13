export type RoleId =
  | "EU Qualified Person"
  | "Chief Quality Officer"
  | "Global Head of Pharmacovigilance"
  | "Chief Medical Officer"
  | "Patient Safety Representative"
  | "Supply Chain VP"
  | "Manufacturing VP";

export interface RoleDef {
  id: RoleId;
  label: string;
  approves: Array<"batch_review" | "pv_intake" | "supply_planning">;
  supplyLeg?: "planning" | "quality";
  canVetoPv?: boolean;
  requesterOnly?: boolean;
  escalation?: boolean;
}

export const ROLES: RoleDef[] = [
  {
    id: "EU Qualified Person",
    label: "EU Qualified Person",
    approves: ["batch_review", "supply_planning"],
    supplyLeg: "quality",
  },
  {
    id: "Chief Quality Officer",
    label: "Chief Quality Officer",
    approves: ["batch_review", "supply_planning"],
    supplyLeg: "quality",
    escalation: true,
  },
  {
    id: "Global Head of Pharmacovigilance",
    label: "Global Head of Pharmacovigilance",
    approves: ["pv_intake"],
  },
  {
    id: "Chief Medical Officer",
    label: "Chief Medical Officer",
    approves: ["pv_intake"],
    escalation: true,
  },
  {
    id: "Patient Safety Representative",
    label: "Patient Safety Representative",
    approves: [],
    canVetoPv: true,
  },
  {
    id: "Supply Chain VP",
    label: "Supply Chain VP",
    approves: ["supply_planning"],
    supplyLeg: "planning",
  },
  {
    id: "Manufacturing VP",
    label: "Manufacturing VP",
    approves: [],
    requesterOnly: true,
  },
];

export const STORAGE_KEY = "aegis.role";

export function roleById(id: string): RoleDef {
  return ROLES.find((r) => r.id === id) ?? ROLES[0];
}

export function canApproveWorkflow(role: RoleDef, workflow: string): boolean {
  if (role.requesterOnly) return false;
  return role.approves.includes(workflow as RoleDef["approves"][number]);
}
