"""Eval harness runner -- loads eval_dataset/*.json, dispatches each
scenario to its grader, compares actual vs expected, produces a scorecard.

What "runs" honestly means at this stage (no apps/ or services/ code
exists -- Stage 20 is deliberately last): this executes real grader logic
against synthetic fixture inputs shaped like our contracts, proving the
GRADING LOGIC is correct. It does not execute a live agentic system,
because none exists. Categories with grading_mode="human_rubric" are
recorded as NOT_APPLICABLE to automated grading, matching V1's own
EVALUATION_PLAN.md ("Evaluation deliverables: ... calibrated human
rubric"). Categories with grading_mode="blocked_by_environment" are
recorded as BLOCKED_BY_ENVIRONMENT, not silently skipped.
"""
import json
import sys
from pathlib import Path

GRADERS_DIR = Path(__file__).resolve().parent
DATASET_DIR = GRADERS_DIR.parent / "eval_dataset"
sys.path.insert(0, str(GRADERS_DIR))
sys.path.insert(0, str(GRADERS_DIR.parent.parent / "quality" / "gates"))

import evidence_authority_grader as eag           # noqa: E402
import prohibited_action_grader as pag            # noqa: E402
import schema_grader as sg                        # noqa: E402
import audit_trail_grader as atg                  # noqa: E402
import pv_duplicate_clock_grader as pdcg           # noqa: E402
import trajectory_grader as tg                     # noqa: E402
import security_grader as secg                     # noqa: E402
import privacy_grader as pg                         # noqa: E402
import subgroup_grader as subg                      # noqa: E402
import latency_cost_grader as lcg                   # noqa: E402
import loop_guard_grader as lgg                      # noqa: E402
import release_gates as rg                            # noqa: E402


def _check(actual, expected):
    """Compares an actual grader-result dict against an expected dict from
    the eval_dataset. Supports exact-match keys and *_contains substring
    checks."""
    for key, exp_val in expected.items():
        if key == "note":
            continue  # documentary commentary, not a check
        if key.endswith("_contains"):
            real_key = key[: -len("_contains")]
            actual_val = str(actual.get(real_key, ""))
            if exp_val not in actual_val:
                return False, f"expected {real_key!r} to contain {exp_val!r}, got {actual_val!r}"
        else:
            if actual.get(key) != exp_val:
                return False, f"expected {key}={exp_val!r}, got {actual.get(key)!r}"
    return True, "ok"


def _grade_scenario(category, scenario):
    inp = scenario.get("input", {})

    if category == "business_outcome":
        return {"gate_state": "NOT_APPLICABLE", "reason": "human_rubric category, no automated grader (matches V1's own EVALUATION_PLAN.md)"}

    if category == "evidence_fidelity_provenance":
        return eag.grade_evidence_fidelity(inp["evidence"], inp["claims"], inp.get("declared_sources"))

    if category == "gxp_safety_boundary":
        return pag.grade_prohibited_action(scenario["workflow"], inp)

    if category == "data_integrity_audit_trail":
        return atg.grade_audit_trail(**inp)

    if category == "retrieval_authority_poisoning_injection":
        return eag.grade_authority(inp["docs"], inp["cited_in_response"], inp.get("instruction_followed_flag", False))

    if category == "structured_output_abstention":
        return sg.grade_schema(inp, scenario["schema_ref"])

    if category == "pv_duplicate_clock_terminology":
        return pdcg.grade_pv_duplicate_clock(**inp)

    if category == "agent_tool_authorization_idempotency":
        if "idempotency_key" in inp:
            return tg.grade_trajectory(**inp)
        return secg.grade_security(**inp)

    if category == "privacy_cross_border":
        return pg.grade_privacy(**inp)

    if category == "subgroup_accessibility":
        result = subg.grade_subgroup_evidence(**inp)
        gaps = result.get("flagged_performance_gaps")
        gate = rg.evaluate_gates({"subgroup": result})
        result["gate_blocked"] = gate["blocked"]
        result["gate_id"] = gate["blocked_by"][0] if gate["blocked_by"] else None
        result["flagged_performance_gaps_nonempty"] = bool(gaps)
        return result

    if category == "latency_cost_denial_of_wallet":
        if "max_cost_per_task_usd" in inp:
            return lcg.grade_cost_threshold(inp["max_cost_per_task_usd"])
        return lcg.grade_latency_cost(**inp)

    if category == "model_substitution_regression":
        if inp.get("route_at_regression_check") == "UNCONFIRMED":
            return {"gate_state": "BLOCKED_BY_ENVIRONMENT", "reason": "ADR-009 LLM-route sub-decision not yet confirmed (trigger T-6)"}
        if "evidence_content_excerpt_before" in inp:
            # Stage 21 gap-closure -- INJ-081: a smaller fallback model preserves schema
            # compliance but loses evidence fidelity in non-English content. The real,
            # verifiable claim: content_excerpt/evidence text is COPIED VERBATIM from the
            # knowledge graph by evidence.retrieve (a deterministic tool, never an LLM
            # call) -- model substitution changes which model writes `synthesize`'s
            # prose, it cannot touch this field at all, in any language. Checked directly
            # rather than assumed.
            fidelity_preserved = inp["evidence_content_excerpt_before"] == inp["evidence_content_excerpt_after"]
            return {
                "pass": fidelity_preserved,
                "reason": "evidence_excerpt_unchanged_by_model_substitution" if fidelity_preserved
                else "evidence_fidelity_regression -- content_excerpt changed across model substitution, which should be structurally impossible",
            }
        ok = (
            inp.get("llm_provider_available") is False
            and inp.get("deterministic_path_completed") is True
            and inp.get("terminal_state") == "abstained"
            and inp.get("abstention_reason") == "degraded_mode"
        )
        return {"pass": ok, "reason": "degraded_mode_continuity_ok" if ok else "degraded_mode_continuity_violated"}

    if category == "agent_wrong_handoff":
        if "critic_context" in inp:
            return tg.grade_critic_context_binding(**inp)
        return tg.grade_critic_routing(**inp)

    if category == "agent_loop_guard_trip":
        if "fingerprints" in inp:
            return lgg.grade_cycle_detection(**inp)
        return lgg.grade_loop_guards(**inp)

    if category == "agent_unauthorized_tool_call":
        return secg.grade_security(**inp)

    return {"pass": False, "reason": f"no dispatch rule for category={category!r}"}


def run_all():
    results = []
    for path in sorted(DATASET_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        category = data["category"]
        for scenario in data["scenarios"]:
            expected = scenario.get("expected", {})
            try:
                actual = _grade_scenario(category, scenario)
            except Exception as exc:  # noqa: BLE001 -- record, don't crash the run
                results.append({
                    "scenario_id": scenario["scenario_id"], "category": category,
                    "status": scenario["status"], "outcome": "ERROR", "detail": repr(exc),
                })
                continue

            if actual.get("gate_state") in {"NOT_APPLICABLE", "BLOCKED_BY_ENVIRONMENT", "THRESHOLD_NOT_DEFINED"}:
                outcome = actual["gate_state"]
                ok, detail = True, actual.get("reason", "")
            else:
                ok, detail = _check(actual, expected)
                outcome = "PASS" if ok else "FAIL"

            results.append({
                "scenario_id": scenario["scenario_id"], "category": category,
                "status": scenario["status"], "outcome": outcome, "detail": detail,
            })
    return results


def print_scorecard(results):
    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    total = len(results)
    passed = sum(1 for r in results if r["outcome"] == "PASS")
    other = {}
    for r in results:
        if r["outcome"] != "PASS":
            other[r["outcome"]] = other.get(r["outcome"], 0) + 1

    print(f"{'CATEGORY':<40} {'SCENARIOS':<10} {'PASS':<6} {'OTHER'}")
    for cat, rows in by_category.items():
        p = sum(1 for r in rows if r["outcome"] == "PASS")
        o = [r for r in rows if r["outcome"] != "PASS"]
        print(f"{cat:<40} {len(rows):<10} {p:<6} {[(x['scenario_id'], x['outcome']) for x in o] if o else ''}")

    print()
    print(f"TOTAL: {total} scenarios, {passed} PASS, breakdown of non-PASS: {other}")

    failures = [r for r in results if r["outcome"] in {"FAIL", "ERROR"}]
    if failures:
        print("\nFAILURES / ERRORS:")
        for r in failures:
            print(f"  {r['scenario_id']} [{r['category']}]: {r['detail']}")
    return failures


if __name__ == "__main__":
    results = run_all()
    failures = print_scorecard(results)
    sys.exit(1 if failures else 0)
