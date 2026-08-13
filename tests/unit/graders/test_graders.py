"""pytest wrapper around eval-ai-cache/graders/run_eval_dataset.py.

Satisfies prompts/18_eval_ai_cache.md's `tests/` output location and exit
criterion "eval harness runs and produces a pass/fail scorecard per
category." One parametrized test per scenario so a single grader
regression shows up as one named test failure, not a monolithic block.
"""
import sys
from pathlib import Path

import pytest

GRADERS_DIR = Path(__file__).resolve().parents[3] / "eval-ai-cache" / "graders"
sys.path.insert(0, str(GRADERS_DIR))

from run_eval_dataset import run_all  # noqa: E402

_RESULTS = run_all()

# States that are correct-by-design non-outcomes, not failures.
_ACCEPTED_NON_PASS = {"NOT_APPLICABLE", "BLOCKED_BY_ENVIRONMENT", "THRESHOLD_NOT_DEFINED"}


@pytest.mark.parametrize(
    "result", _RESULTS, ids=[r["scenario_id"] for r in _RESULTS]
)
def test_scenario(result):
    if result["outcome"] in _ACCEPTED_NON_PASS:
        pytest.skip(f"{result['outcome']}: {result['detail']}")
    assert result["outcome"] == "PASS", result["detail"]


def test_no_unaccounted_categories():
    """Every category in eval_dataset/ must have produced at least one
    result -- catches a silently-unhandled category (a dispatch gap) that
    would otherwise show up as zero scenarios rather than a failure."""
    categories = {r["category"] for r in _RESULTS}
    assert len(categories) == 15, f"expected 15 categories, got {len(categories)}: {sorted(categories)}"
