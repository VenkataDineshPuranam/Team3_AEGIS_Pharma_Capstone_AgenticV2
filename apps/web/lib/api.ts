const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Workflow = "batch_review" | "pv_intake" | "supply_planning";

export interface DraftClaim {
  text: string;
  cites: string[];
}

export interface EvidenceItem {
  evidence_id: string;
  source: string;
  status: string;
  effective_date?: string | null;
  jurisdiction?: string | null;
  supersedes?: string | null;
  content_excerpt?: string;
}

export interface ReconciliationFinding {
  category: string;
  status: "complete" | "gap" | "conflict";
  evidence_ids: string[];
  gap_description?: string | null;
}

export interface DuplicateCandidate {
  candidate_case_id: string;
  similarity_score: number;
  matched_fields: string[];
}

export interface NormalizationSuggestion {
  normalized_term: string;
  confidence: number;
  terminology_source: string;
}

export interface ShortageOption {
  option_id: string;
  description: string;
  constraints_satisfied: string[];
  cold_chain_evidence_ids: string[];
  transport_notes: string;
}

export interface DomainPayload {
  batch_id?: string;
  reconciliation_complete?: boolean;
  findings?: ReconciliationFinding[];
  case_id?: string;
  duplicate_suspected?: boolean;
  candidates?: DuplicateCandidate[];
  normalization_suggestions?: NormalizationSuggestion[];
  product_id?: string;
  options?: ShortageOption[];
  constraint_set?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface AuditEvent {
  kind: string;
  [key: string]: unknown;
}

export interface QueueEntry {
  run_id: string;
  workflow: Workflow;
  subject_id: string;
  requester_role: string;
  approver_roles: string[];
  required_legs: string[] | null;
  approved_legs: string[];
  draft_summary: string | null;
  draft_claims: DraftClaim[];
  created_at: string;
  hitl_tier?: string | null;
  hitl_deadline?: string | null;
  policy_contract_version?: string | null;
  critic_reason_codes?: string[];
  snapshot?: Partial<RunResult>;
}

export interface RunResult {
  run_id: string;
  workflow: Workflow;
  subject_id?: string | null;
  requester_role?: string | null;
  status:
    | "pending_approval"
    | "completed"
    | "abstained"
    | "blocked"
    | "refused"
    | "timed_out";
  terminal_state: string | null;
  abstention_reason: string | null;
  llm_calls: number | null;
  tool_calls?: number | null;
  tokens_in?: number | null;
  tokens_out?: number | null;
  draft_summary: string | null;
  draft_claims: DraftClaim[];
  approver_roles: string[];
  required_legs: string[] | null;
  approved_legs: string[];
  policy_contract_version?: string | null;
  hitl_status?: string | null;
  hitl_tier?: string | null;
  hitl_deadline?: string | null;
  veto_recorded?: boolean;
  evidence?: EvidenceItem[];
  domain_payload?: DomainPayload | null;
  critic_verdict?: string | null;
  critic_reason_codes?: string[];
  guard_verdict?: string | null;
  trace_id?: string | null;
  created_at?: string | null;
  audit_events?: AuditEvent[];
}

export interface DashboardResponse {
  workflow: string | null;
  cost: {
    run_count: number;
    mean_tokens_per_run: number | null;
    p95_tokens_per_run: number | null;
    mean_llm_calls_per_run: number | null;
  };
  guardrail_trip: {
    run_count: number;
    blocked_count: number;
    blocked_rate: number | null;
  };
  terminal_states: {
    run_count: number;
    by_terminal_state: Record<string, number>;
    by_abstention_reason: Record<string, number>;
  };
  cache: {
    hits: number | null;
    misses: number | null;
    hit_rate: number | null;
    status?: string;
  };
}

export interface HealthResponse {
  status: string;
  workflows: string[];
  dependencies: Record<string, { ok: boolean; detail?: string; mode?: string }>;
}

export interface GuardrailEvent {
  run_id: string;
  workflow?: string | null;
  matched_terms: string[];
  draft_sha256?: string | null;
  recorded_at?: string | null;
  abstention_reason?: string | null;
}

export interface GovernanceResponse {
  policy_engine_ok: boolean;
  policy_contract_version: string | null;
  detail: string;
  hitl_ladder: Record<string, unknown>;
  prohibition_workflows: string[];
  note: string;
}

let currentRole: string | null = null;

export function setApiRole(role: string | null) {
  currentRole = role;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (currentRole) headers["X-Approver-Role"] = currentRole;
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export function getQueue(workflow?: Workflow): Promise<QueueEntry[]> {
  const qs = workflow ? `?workflow=${workflow}` : "";
  return request(`/api/queue${qs}`);
}

export function getRun(runId: string): Promise<RunResult> {
  return request(`/api/runs/${runId}`);
}

export function listRuns(opts?: { workflow?: Workflow; status?: string }): Promise<RunResult[]> {
  const params = new URLSearchParams();
  if (opts?.workflow) params.set("workflow", opts.workflow);
  if (opts?.status) params.set("status", opts.status);
  const qs = params.toString() ? `?${params}` : "";
  return request(`/api/runs${qs}`);
}

export function submitRun(body: {
  workflow: Workflow;
  subject_id: string;
  requester_role: string;
}): Promise<RunResult> {
  return request("/api/runs", { method: "POST", body: JSON.stringify(body) });
}

export function decideRun(
  runId: string,
  body: {
    workflow: Workflow;
    action: "approved" | "rejected" | "veto" | "timed_out";
    leg?: "planning" | "quality";
    justification?: string;
  },
): Promise<RunResult> {
  return request(`/api/runs/${runId}/decide`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getDashboard(workflow?: Workflow): Promise<DashboardResponse> {
  const qs = workflow ? `?workflow=${workflow}` : "";
  return request(`/api/dashboard${qs}`);
}

export function getHealth(): Promise<HealthResponse> {
  return request("/api/health");
}

export function getGuardrails(): Promise<GuardrailEvent[]> {
  return request("/api/guardrails");
}

export function getGovernance(): Promise<GovernanceResponse> {
  return request("/api/governance");
}
