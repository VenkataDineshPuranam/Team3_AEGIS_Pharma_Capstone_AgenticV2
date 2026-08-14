"""services/integration/hitl_timer.py -- the read-time severity/timer computation shown
in the Decision Queue and Decision Detail UI. Display only; does not affect who is
authorized to decide a run (that stays user_store.approver_string_for, unchanged).

Thresholds are per-workflow (docs/governance/hitl_control_model.md SS7) -- Batch Review
and Supply Planning use 8h/16h/24h, PV Intake uses the deliberately shorter 4h/8h/24h.
Most tests below use batch_review as the representative workflow; a dedicated section
covers PV Intake's distinct ladder.
"""
from datetime import UTC, datetime, timedelta

from services.integration import hitl_timer


def _created_at(hours_ago: float) -> str:
    return (datetime.now(UTC) - timedelta(hours=hours_ago)).isoformat()


def test_a_freshly_created_entry_is_tier_t0():
    result = hitl_timer.compute(_created_at(0), "batch_review")
    assert result.tier == "T0"
    assert result.severity == 1
    assert abs(result.hours_to_next_tier - 8) < 0.01


def test_just_under_eight_hours_is_still_t0():
    result = hitl_timer.compute(_created_at(7.9), "batch_review")
    assert result.tier == "T0"


def test_eight_hours_elapsed_is_t1_reminder():
    result = hitl_timer.compute(_created_at(8), "batch_review")
    assert result.tier == "T1"
    assert result.label == "Reminder due"
    assert result.severity == 2


def test_sixteen_hours_elapsed_is_t2_escalation():
    result = hitl_timer.compute(_created_at(16), "batch_review")
    assert result.tier == "T2"
    assert result.label == "Escalation due"
    assert result.severity == 3


def test_twenty_four_hours_elapsed_is_t3_expired_with_no_next_tier():
    result = hitl_timer.compute(_created_at(24), "batch_review")
    assert result.tier == "T3"
    assert result.label == "Expired"
    assert result.severity == 4
    assert result.hours_to_next_tier is None


def test_severity_increases_monotonically_with_tier():
    severities = [hitl_timer.compute(_created_at(h), "batch_review").severity for h in (0, 8, 16, 24)]
    assert severities == sorted(severities)
    assert severities == [1, 2, 3, 4]


def test_well_past_expiry_stays_t3_not_a_new_tier():
    result = hitl_timer.compute(_created_at(1000), "batch_review")
    assert result.tier == "T3"


def test_hours_elapsed_is_computed_correctly():
    result = hitl_timer.compute(_created_at(3.5), "batch_review")
    assert abs(result.hours_elapsed - 3.5) < 0.01


def test_accepts_a_naive_iso_timestamp_by_assuming_utc():
    naive = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None).isoformat()
    result = hitl_timer.compute(naive, "batch_review")
    assert result.tier == "T0"
    assert abs(result.hours_elapsed - 1) < 0.05


# --- per-workflow ladder (hitl_control_model.md SS7) -------------------------------


def test_supply_planning_uses_the_same_ladder_as_batch_review():
    for h, expected_tier in ((0, "T0"), (8, "T1"), (16, "T2"), (24, "T3")):
        assert hitl_timer.compute(_created_at(h), "supply_planning").tier == expected_tier


def test_pv_intake_uses_a_shorter_ladder_than_batch_review():
    """SS7: PV Intake is 4h/8h/24h, deliberately shorter than Batch Review's 8h/16h/24h,
    because a real regulatory reporting clock is at stake."""
    assert hitl_timer.compute(_created_at(0), "pv_intake").tier == "T0"
    assert hitl_timer.compute(_created_at(4), "pv_intake").tier == "T1"
    assert hitl_timer.compute(_created_at(8), "pv_intake").tier == "T2"
    assert hitl_timer.compute(_created_at(24), "pv_intake").tier == "T3"


def test_at_eight_hours_pv_intake_and_batch_review_disagree():
    """The exact bug this test guards against: an earlier version of hitl_timer.py used
    Batch Review's ladder for every workflow, which understated PV Intake's urgency -- at
    8h elapsed, Batch Review is only just reaching T1 while PV Intake should already be at
    its final tier, T2."""
    created = _created_at(8)
    assert hitl_timer.compute(created, "batch_review").tier == "T1"
    assert hitl_timer.compute(created, "pv_intake").tier == "T2"


def test_the_three_stage_21_workflows_fall_back_to_the_batch_review_ladder():
    """Not specified in hitl_control_model.md -- these three workflows postdate it. The
    fallback is an explicit, documented assumption, not a researched duration."""
    for workflow in ("research_review", "clinical_integrity", "regulatory_completeness"):
        assert hitl_timer.compute(_created_at(8), workflow).tier == "T1"
        assert hitl_timer.compute(_created_at(16), workflow).tier == "T2"


def test_an_unrecognized_workflow_falls_back_to_the_default_ladder_rather_than_erroring():
    result = hitl_timer.compute(_created_at(8), "some_future_workflow")
    assert result.tier == "T1"
