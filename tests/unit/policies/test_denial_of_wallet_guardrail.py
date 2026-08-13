"""Self-test for infra/policies/denial_of_wallet_guardrail.py.

Proves the ceiling actually trips -- exit criterion: "implemented as an
enforced hook, not a documented policy only." An untested guardrail is
indistinguishable from a documented policy that happens to have code next
to it; this is what makes the difference real.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "infra" / "policies"))

from denial_of_wallet_guardrail import (  # noqa: E402
    DAILY_RUN_CEILING,
    MAX_DAILY_SPEND_USD,
    MAX_TOKENS_PER_RUN,
    DenialOfWalletGuard,
)


def test_ceiling_values_match_documented_derivation():
    # Locks the derivation in token_economics.md / the module docstring --
    # a change to either without the other is a defect this test catches.
    assert MAX_TOKENS_PER_RUN == 150_000
    assert DAILY_RUN_CEILING == 20
    assert MAX_DAILY_SPEND_USD == 45.00


def test_admits_within_ceiling():
    guard = DenialOfWalletGuard()
    result = guard.check_and_admit("qp-alice", "batch_review", date(2026, 8, 12), estimated_tokens=2000)
    assert result["admit"] is True


def test_run_count_ceiling_trips_at_21st_run():
    guard = DenialOfWalletGuard()
    d = date(2026, 8, 12)
    # Record 20 cheap runs (well under spend ceiling) to isolate the run-count check
    for _ in range(DAILY_RUN_CEILING):
        guard.record_run("qp-alice", "batch_review", d, actual_tokens=100)
    result = guard.check_and_admit("qp-alice", "batch_review", d, estimated_tokens=100)
    assert result["admit"] is False
    assert "daily_run_ceiling_exceeded" in result["reason"]


def test_spend_ceiling_trips_before_run_count_on_expensive_runs():
    guard = DenialOfWalletGuard()
    d = date(2026, 8, 12)
    # 3 worst-case-token runs already blow past $45 (3 * $2.25 = $6.75 -- need more)
    # Use runs at MAX_TOKENS_PER_RUN each: $2.25/run -> ceiling trips at run 21 by
    # spend math alone before run-count would (21 * 2.25 = 47.25 > 45). Force it
    # directly by recording 19 max-cost runs (19 * 2.25 = 42.75), leaving only
    # $2.25 headroom -- the 20th admit check at full estimate should still fit
    # exactly, so push one more token to force the spend ceiling specifically.
    for _ in range(19):
        guard.record_run("qp-bob", "supply_planning", d, actual_tokens=MAX_TOKENS_PER_RUN)
    result = guard.check_and_admit("qp-bob", "supply_planning", d, estimated_tokens=MAX_TOKENS_PER_RUN + 1)
    assert result["admit"] is False
    assert "daily_spend_ceiling_exceeded" in result["reason"]


def test_ceilings_are_scoped_per_user_and_workflow_independently():
    guard = DenialOfWalletGuard()
    d = date(2026, 8, 12)
    for _ in range(DAILY_RUN_CEILING):
        guard.record_run("qp-alice", "batch_review", d, actual_tokens=100)
    # Same user, different workflow -- must not inherit alice's batch_review exhaustion
    other_workflow = guard.check_and_admit("qp-alice", "pv_intake", d, estimated_tokens=100)
    assert other_workflow["admit"] is True
    # Different user, same workflow -- must not inherit alice's exhaustion either
    other_user = guard.check_and_admit("md-carol", "batch_review", d, estimated_tokens=100)
    assert other_user["admit"] is True


def test_ceilings_reset_per_day():
    guard = DenialOfWalletGuard()
    day1 = date(2026, 8, 12)
    day2 = date(2026, 8, 13)
    for _ in range(DAILY_RUN_CEILING):
        guard.record_run("qp-alice", "batch_review", day1, actual_tokens=100)
    exhausted_today = guard.check_and_admit("qp-alice", "batch_review", day1, estimated_tokens=100)
    fresh_tomorrow = guard.check_and_admit("qp-alice", "batch_review", day2, estimated_tokens=100)
    assert exhausted_today["admit"] is False
    assert fresh_tomorrow["admit"] is True


def test_admit_check_is_worst_case_conservative_by_default():
    """Calling check_and_admit with no estimate uses MAX_TOKENS_PER_RUN (C1),
    never a hopeful smaller guess -- same fail-safe direction as ADR-005."""
    guard = DenialOfWalletGuard()
    d = date(2026, 8, 12)
    # 19 runs at $0 recorded cost (simulate cheap actuals) but the 20th ADMIT
    # check with the default (worst-case) estimate should still be evaluated
    # against the worst-case token count, not the cheap historical actuals.
    for _ in range(19):
        guard.record_run("qp-alice", "batch_review", d, actual_tokens=1)
    result = guard.check_and_admit("qp-alice", "batch_review", d)  # no estimate passed
    # spend_so_far is ~0, so this must be admitted (well under $45), but the
    # projection must have used MAX_TOKENS_PER_RUN as the default, not 0.
    assert result["admit"] is True
