"""Stage 21 -- the structured HITL decision payload that closes the G-10 justification gap.

The property that matters most here is the boring one: every pre-Stage-21 resume shape
still means exactly what it meant before. The rest of this repo's test suite resumes the
three graphs with bare strings and {"leg","action"} dicts, and those tests are what prove
the veto, dual-approval, and timeout guarantees. If `decode` reinterpreted any of them,
those proofs would silently stop covering the paths they claim to.
"""

from packages.domain.hitl_decision import LEGACY_PLACEHOLDER, decode


def test_bare_string_resume_still_means_what_it_meant():
    for action in ("approved", "rejected", "veto", "timed_out"):
        decision = decode(action)
        assert decision.action == action
        assert decision.leg is None
        assert decision.claimed_identity is None


def test_bare_string_carries_the_placeholder_not_a_forged_human_justification():
    """A harness-originated resume must not produce a record that reads like a human
    wrote a rationale. The placeholder is honest labelling, not a workaround for
    write_human_override's non-empty check."""
    assert decode("approved").justification == LEGACY_PLACEHOLDER
    assert "no structured justification" in LEGACY_PLACEHOLDER


def test_legacy_supply_dual_approval_dict_still_decodes():
    decision = decode({"leg": "quality", "action": "approved"})
    assert decision.action == "approved"
    assert decision.leg == "quality"
    assert decision.justification == LEGACY_PLACEHOLDER


def test_structured_payload_carries_the_humans_own_words():
    decision = decode({
        "action": "rejected",
        "justification": "Deviation DEV-14 is unresolved; the release packet is incomplete.",
        "claimed_identity": "qp@example.test",
        "leg": None,
    })
    assert decision.action == "rejected"
    assert decision.justification == "Deviation DEV-14 is unresolved; the release packet is incomplete."
    assert decision.claimed_identity == "qp@example.test"


def test_blank_or_whitespace_justification_falls_back_to_the_placeholder():
    """audit_store.write_human_override rejects an empty justification outright. Decoding
    whitespace to the placeholder keeps that check meaningful rather than letting a blank
    field masquerade as a filled one -- the API's own min_length is the real gate."""
    for blank in ("", "   ", "\n\t"):
        assert decode({"action": "approved", "justification": blank}).justification == LEGACY_PLACEHOLDER


def test_unrecognized_payload_yields_no_action_rather_than_guessing():
    """An action the graphs don't recognize routes to their non-approval paths. Guessing
    'approved' from a malformed payload is the one failure this must never have."""
    for garbage in (None, 42, ["approved"], object()):
        assert decode(garbage).action == ""


def test_claimed_identity_is_never_treated_as_a_role():
    """The field exists to be recorded as context. Nothing in the decision object exposes
    it as an approver role -- the graphs write their own governance-determined role."""
    decision = decode({"action": "approved", "justification": "x" * 20, "claimed_identity": "Chief Quality Officer"})
    assert decision.claimed_identity == "Chief Quality Officer"
    assert not hasattr(decision, "approver_roles")
    assert not hasattr(decision, "role")
