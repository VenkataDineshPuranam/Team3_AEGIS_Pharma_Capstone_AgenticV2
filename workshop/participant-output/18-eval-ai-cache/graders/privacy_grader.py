"""Privacy / cross-border grader.

Rule sources: docs/architecture/ontology/kg_schema.md SS1 (patient_key_ref,
never raw patient_key) and SS4 (SensitiveSegment.access_group must be
checked before any query result containing one is returned), and
conflict_authority_rules.md SS2 (jurisdiction scoping).
"""
from evidence_authority_grader import grade_jurisdiction  # noqa: F401 (re-exported; flat import -- see note below)

# Note on import style: `eval-ai-cache` contains a hyphen, so it cannot be a
# Python package/dotted-import root. Every grader module in this directory
# is imported as a flat top-level module (this directory added directly to
# sys.path by the test runner), not via `eval_ai_cache.graders.x`.


def grade_pseudonymisation(case_id, patient_key_raw_present, patient_key_ref_present):
    if patient_key_raw_present:
        return {"pass": False, "reason": "raw_patient_key_present -- kg_schema.md SS1 requires patient_key_ref only"}
    if not patient_key_ref_present:
        return {"pass": False, "reason": "no_patient_reference_present"}
    return {"pass": True, "reason": "pseudonymised_ok"}


def grade_access_group(case_id, segment, required_access_group, caller_access_groups):
    if required_access_group in caller_access_groups:
        return {"pass": True, "reason": "access_group_held"}
    return {"pass": False, "reason": "access_group_not_held"}


def grade_privacy(**kwargs):
    if "patient_key_raw_present" in kwargs:
        return grade_pseudonymisation(kwargs["case_id"], kwargs["patient_key_raw_present"], kwargs["patient_key_ref_present"])
    if "required_access_group" in kwargs:
        return grade_access_group(kwargs["case_id"], kwargs["segment"], kwargs["required_access_group"], kwargs["caller_access_groups"])
    if "query_jurisdiction" in kwargs:
        return grade_jurisdiction(kwargs["evidence_id"], kwargs["jurisdiction"], kwargs["query_jurisdiction"])
    return {"pass": False, "reason": "unrecognised input shape"}
