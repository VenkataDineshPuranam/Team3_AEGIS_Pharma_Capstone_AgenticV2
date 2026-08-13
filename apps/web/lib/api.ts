// Typed fetch client for the Orchestrator API (services/api/main.py).
// Base URL from NEXT_PUBLIC_API_URL, defaulting to the local FastAPI dev server.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Workflow = "batch_review" | "pv_intake" | "supply_planning";

export interface DraftClaim {
  text: string;
  cites: string[];
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
}

export interface RunResult {
  run_id: string;
  workflow: Workflow;
  status:
    | "pending_approval"
    | "completed"
    | "abstained"
    | "blocked"
    | "refused";
  terminal_state: string | null;
  abstention_reason: string | null;
  llm_calls: number | null;
  draft_summary: string | null;
  draft_claims: DraftClaim[];
  approver_roles: string[];
  required_legs: string[] | null;
  approved_legs: string[];
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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
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
