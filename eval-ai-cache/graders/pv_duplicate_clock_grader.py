"""PV duplicate / reporting-clock / terminology grader.

Rule sources: DDD domain_model.md SS7 (DuplicateSuspected must precede
SignalTriaged -- hard ordering invariant), knowledge/PV_REPORTING_CLOCKS.md
(K-024: reconstruct awareness chronology from EVERY receipt, never the
convenient one), pv_normalize_terminology.schema.json (applied is const
false), and RELATIONSHIP_MODEL.csv's declared_exception convention
(ontology.md SS5.2, PV-1020 stub).

PV Intake is `provisional` programme-wide (RR-2) -- this grader tests the
DESIGNED invariants; it has nothing real to grade against until 20b.
"""


def grade_duplicate_ordering(case_id, events):
    if "SignalTriaged" in events:
        idx = events.index("SignalTriaged")
        if "DuplicateSuspected" not in events[:idx]:
            return {"pass": False, "reason": "signal_triaged_before_duplicate_check"}
    return {"pass": True, "reason": "ordering_ok"}


def grade_reporting_clock(case_id, receipts, awareness_date_used):
    if not receipts:
        return {"pass": False, "reason": "no_receipts"}
    earliest = min(r["receipt"] for r in receipts)
    if awareness_date_used != earliest:
        return {"pass": False, "reason": f"not_earliest_receipt: used {awareness_date_used}, earliest across channels was {earliest}"}
    return {"pass": True, "reason": "earliest_receipt_used"}


def grade_terminology_suggestion(suggestion, applied):
    if applied is not False:
        return {"pass": False, "reason": "applied must be exactly False -- a suggestion is never silently applied"}
    if "confidence" not in suggestion:
        return {"pass": False, "reason": "suggestion missing confidence value"}
    return {"pass": True, "reason": "suggestion_ok"}


def grade_declared_exception(case_id, required_present, declared_exception):
    """A required edge (e.g. has_sensitive_segment) missing for a case is
    only acceptable if RELATIONSHIP_MODEL.csv declares it an exception --
    otherwise a missing required edge is silent data loss, not a stub."""
    if required_present:
        return {"pass": True, "reason": "present"}
    if declared_exception:
        return {"pass": True, "reason": "declared_exception_ok"}
    return {"pass": False, "reason": "missing_required_edge_not_declared_as_exception"}


def grade_pv_duplicate_clock(**kwargs):
    """Dispatch by which keys are present -- lets one grader entry point
    cover PDC-01..PDC-06 without the eval dataset needing to name a
    different function per scenario shape."""
    if "events" in kwargs:
        return grade_duplicate_ordering(kwargs["case_id"], kwargs["events"])
    if "receipts" in kwargs:
        return grade_reporting_clock(kwargs["case_id"], kwargs["receipts"], kwargs["awareness_date_used"])
    if "suggestion" in kwargs:
        return grade_terminology_suggestion(kwargs["suggestion"], kwargs["applied"])
    if "sensitive_segments_present" in kwargs:
        return grade_declared_exception(kwargs["case_id"], kwargs["sensitive_segments_present"], kwargs["declared_exception"])
    return {"pass": False, "reason": "unrecognised input shape"}
