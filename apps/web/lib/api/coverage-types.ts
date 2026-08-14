/** Wire types for /api/evals/scorecard and /api/coverage/injects. */

export interface EvalScenario {
  scenario_id: string;
  status: string;
  outcome: string;
  detail: string;
  is_failure: boolean;
}

export interface EvalCategory {
  category: string;
  scenario_count: number;
  passed: number;
  failed: number;
  non_pass_accepted: number;
  scenarios: EvalScenario[];
}

export interface EvalScorecard {
  total_scenarios: number;
  passed: number;
  failed: number;
  accepted_non_pass: number;
  category_count: number;
  categories: EvalCategory[];
  source: string;
}

export type CoverageStatus = "COVERED" | "PARTIAL" | "OUT_OF_SCOPE" | "NOT_COVERED";

export interface Inject {
  id: string;
  dimension: string;
  title: string;
  scenario: string;
  v2_evidence_sources: string;
  status: CoverageStatus;
  rationale: string;
}

export interface CoverageDimension {
  id: string;
  title: string;
  test_class: string;
  release_gate: string;
  inject_count: number;
  by_status: Partial<Record<CoverageStatus, number>>;
}

export interface InjectCoverage {
  methodology: string;
  source_dataset: string;
  reviewed_at: string;
  total_injects: number;
  by_status: Partial<Record<CoverageStatus, number>>;
  dimensions: CoverageDimension[];
  injects: Inject[];
}
