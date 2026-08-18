"""Human-precedent authority grader (ADR-010).

A cited HP-* item is a similar-gap fact. This grader fails if:
  - a claim cites a superseded HP-* id (ADR-003 still applies)
  - the draft carries an approval/disposition-shaped field
It does not replace prohibited_action_grader / prohibited_action_guard for
"reject the batch because of precedent" prose -- that remains a banned-term hit.
"""

_MUST_NOT_CITE = {"untrusted", "superseded"}
_APPROVAL_SHAPED_FIELDS = {
    "release_recommended",
    "reject_recommended",
    "auto_approved",
    "disposition",
}


def grade_precedent_authority(evidence, claims, draft_fields=None):
    """evidence: list of {evidence_id, status, source?}. claims: list of {text, cites}."""
    violations = []
    status_by_id = {d["evidence_id"]: d.get("status") for d in evidence}
    for claim in claims:
        for eid in claim.get("cites") or []:
            if str(eid).startswith("HP-") and status_by_id.get(eid) in _MUST_NOT_CITE:
                violations.append(f"cited_despite_{status_by_id[eid]}:{eid}")
    dumped = draft_fields or {}
    for name in _APPROVAL_SHAPED_FIELDS:
        if name in dumped:
            violations.append(f"approval_shaped_field:{name}")
    ok = not violations
    return {"pass": ok, "reason": "precedent_authority_ok" if ok else ";".join(violations)}
