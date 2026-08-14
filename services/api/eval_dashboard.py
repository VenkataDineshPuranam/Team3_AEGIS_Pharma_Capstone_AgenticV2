"""Evaluation & Security Coverage read model -- Stage 21.

Two genuinely different datasets, kept apart rather than blended into one fake "coverage
score":

  1. eval_scorecard() -- calls eval-ai-cache's own run_all() directly, in-process. This is
     real, LIVE grading logic (~25ms, no LLM/network calls -- it grades synthetic fixture
     inputs against the same graders tests/unit/graders/test_graders.py uses), not a cached
     snapshot. Every page load reflects the actual current state of the grader code.

  2. inject_coverage() -- reads a CURATED, versioned JSON file
     (evidence/quality-gates/inject_coverage_v2_to_v3.json). This is NOT computed at
     request time: whether V3 "covers" a V2 tabletop-exercise inject is a judgment call
     that requires reading and understanding code, not something a script can determine by
     pattern-matching. The file is the recorded output of that human-reviewed analysis,
     with real file citations for every non-OUT_OF_SCOPE verdict -- served as-is, not
     regenerated, per the same "backend script produces the artifact, dashboard reads it"
     split used for the eval scorecard's own design (eval-ai-cache/scorecard.md).

Both are honest about the difference between a document and a live signal: eval_scorecard
is the only piece of this file that can print DIFFERENT numbers than yesterday's page load.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INJECT_COVERAGE_PATH = REPO_ROOT / "evidence" / "quality-gates" / "inject_coverage_v2_to_v3.json"

_GRADERS_DIR = REPO_ROOT / "eval-ai-cache" / "graders"
_GATES_DIR = REPO_ROOT / "quality" / "gates"


class InjectCoverageUnavailable(RuntimeError):
    pass


def eval_scorecard() -> dict:
    """Runs the real eval-ai-cache harness in-process and returns a structured scorecard.

    Mirrors tests/unit/graders/test_graders.py's own accepted-non-pass set -- a category
    graded NOT_APPLICABLE/BLOCKED_BY_ENVIRONMENT/THRESHOLD_NOT_DEFINED is not a failure,
    it is a correct-by-design non-outcome (e.g. business_outcome has no automated grader
    by design, matching V2's own EVALUATION_PLAN.md).
    """
    for path in (_GRADERS_DIR, _GATES_DIR):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from run_eval_dataset import run_all  # local import -- path must be set up first

    results = run_all()
    accepted_non_pass = {"NOT_APPLICABLE", "BLOCKED_BY_ENVIRONMENT", "THRESHOLD_NOT_DEFINED"}

    by_category: dict[str, list[dict]] = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    categories = []
    for cat, rows in sorted(by_category.items()):
        passed = sum(1 for r in rows if r["outcome"] == "PASS")
        failed = sum(1 for r in rows if r["outcome"] not in accepted_non_pass | {"PASS"})
        categories.append({
            "category": cat,
            "scenario_count": len(rows),
            "passed": passed,
            "failed": failed,
            "non_pass_accepted": len(rows) - passed - failed,
            "scenarios": [
                {
                    "scenario_id": r["scenario_id"],
                    "status": r["status"],
                    "outcome": r["outcome"],
                    "detail": r["detail"],
                    "is_failure": r["outcome"] not in accepted_non_pass | {"PASS"},
                }
                for r in rows
            ],
        })

    total = len(results)
    passed_total = sum(1 for r in results if r["outcome"] == "PASS")
    failed_total = sum(1 for r in results if r["outcome"] not in accepted_non_pass | {"PASS"})

    return {
        "total_scenarios": total,
        "passed": passed_total,
        "failed": failed_total,
        "accepted_non_pass": total - passed_total - failed_total,
        "category_count": len(categories),
        "categories": categories,
        "source": "eval-ai-cache/graders/run_eval_dataset.py:run_all() -- executed live, this request",
    }


def inject_coverage() -> dict:
    """The curated 84-inject V2-to-V3 coverage mapping. See module docstring for why this
    is read from a file rather than computed -- an ANALYSIS this specific cannot be
    reliably re-derived by a script on every request without becoming exactly the kind of
    fabricated metric Phase 5 prohibits."""
    if not INJECT_COVERAGE_PATH.exists():
        raise InjectCoverageUnavailable(f"{INJECT_COVERAGE_PATH} does not exist.")
    try:
        data = json.loads(INJECT_COVERAGE_PATH.read_text())
    except json.JSONDecodeError as exc:
        raise InjectCoverageUnavailable(f"{INJECT_COVERAGE_PATH} is not valid JSON: {exc}") from exc

    injects = data["injects"]
    by_status: dict[str, int] = {}
    for item in injects:
        by_status[item["status"]] = by_status.get(item["status"], 0) + 1

    by_dimension = []
    dims = {d["id"]: d for d in data["dimensions"]}
    for dim_id, dim in dims.items():
        dim_injects = [i for i in injects if i["dimension"] == dim_id]
        dim_status: dict[str, int] = {}
        for item in dim_injects:
            dim_status[item["status"]] = dim_status.get(item["status"], 0) + 1
        by_dimension.append({**dim, "inject_count": len(dim_injects), "by_status": dim_status})

    return {
        "methodology": data["methodology"],
        "source_dataset": data["source_dataset"],
        "reviewed_at": data["reviewed_at"],
        "total_injects": len(injects),
        "by_status": by_status,
        "dimensions": by_dimension,
        "injects": injects,
    }
