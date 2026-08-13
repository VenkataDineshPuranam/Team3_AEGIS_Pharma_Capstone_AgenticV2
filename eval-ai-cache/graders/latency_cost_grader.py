"""Latency / cost / denial-of-wallet grader.

Rule source: docs/architecture/agentic/failure_and_loop_guards.md SS3 --
safety CEILINGS (C1-C4), derived from graph shape, checkable now. These are
explicitly NOT Stage 15 BUDGETS (numeric targets from measured data); a
ceiling breach means a structural cap already failed to hold, which is a
graph defect, not a cost-tuning signal.
"""

CEILINGS = {
    "C1_tokens_per_run": 150_000,
    "C2_tokens_per_call": 40_000,
    "G1_max_llm_calls": 6,
}


def grade_latency_cost(llm_calls, tokens_total, max_single_call_tokens):
    if llm_calls > CEILINGS["G1_max_llm_calls"]:
        return {"pass": False, "reason": f"structural_cap_exceeded: llm_calls={llm_calls} > G1 cap {CEILINGS['G1_max_llm_calls']}"}
    if tokens_total > CEILINGS["C1_tokens_per_run"]:
        return {"pass": False, "reason": f"ceiling_exceeded: tokens_total={tokens_total} > C1 {CEILINGS['C1_tokens_per_run']}"}
    if max_single_call_tokens > CEILINGS["C2_tokens_per_call"]:
        return {"pass": False, "reason": f"ceiling_exceeded: max_single_call_tokens={max_single_call_tokens} > C2 {CEILINGS['C2_tokens_per_call']}"}
    return {"pass": True, "reason": "within_structural_ceilings"}


def compute_cost_per_successful_task(usage_row, cost_row):
    """Kept for parity with V2's latency_cost_grader.py pattern -- usable
    once real usage/cost rows exist (Stage 15). Not exercised by any
    passing scenario in this stage's dataset; LCD-04 deliberately routes
    through grade_cost_threshold below instead, since the number to check
    against does not exist yet (U1, Unknown since Stage 01)."""
    input_tokens = float(usage_row["input_tokens"])
    output_tokens = float(usage_row["output_tokens"])
    successful = float(usage_row["successful_tasks"])
    input_cost = input_tokens / 1_000_000 * float(cost_row["input_per_million"])
    output_cost = output_tokens / 1_000_000 * float(cost_row["output_per_million"])
    if successful <= 0:
        return None
    return round((input_cost + output_cost) / successful, 4)


def grade_cost_threshold(max_cost_per_task_usd):
    if max_cost_per_task_usd is None:
        return {"gate_state": "THRESHOLD_NOT_DEFINED", "reason": "U1 (token/cost per run) is Unknown until interim assumption 6 is measured at 20a; setting a number now would be guessing (BC-13)"}
    return {"pass": True, "gate_state": "PASS"}
