const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Workflow = "batch_review" | "pv_intake" | "supply_planning";

export interface RunResult {
  run_id: string;
  workflow: Workflow;
  subject_id?: string | null;
  status: string;
  terminal_state: string | null;
  abstention_reason: string | null;
  llm_calls: number | null;
  tool_calls?: number | null;
  tokens_in?: number | null;
  tokens_out?: number | null;
  critic_reason_codes?: string[];
  policy_contract_version?: string | null;
  trace_id?: string | null;
  created_at?: string | null;
  guard_verdict?: string | null;
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

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const getHealth = () => request<HealthResponse>("/api/health");
export const getDashboard = (workflow?: Workflow) =>
  request<DashboardResponse>(`/api/dashboard${workflow ? `?workflow=${workflow}` : ""}`);
export const listRuns = () => request<RunResult[]>("/api/runs");
export const getRun = (id: string) => request<RunResult>(`/api/runs/${id}`);
export const getGuardrails = () => request<GuardrailEvent[]>("/api/guardrails");
export const getGovernance = () => request<GovernanceResponse>("/api/governance");
