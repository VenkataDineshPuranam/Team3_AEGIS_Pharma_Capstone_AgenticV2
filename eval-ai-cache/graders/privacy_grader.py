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


def grade_reidentification_risk(dataset_id, quasi_identifiers_present, safe_combination_threshold=2):
    """Stage 21 gap-closure -- INJ-059: a 'pseudonymised' dataset that still carries
    enough quasi-identifiers in combination (rare disease + region + age-band + sex,
    etc.) is re-identifiable even with no raw patient key present. GENOMIC_DATA_STANDARD.md's
    enhanced-controls requirement is this: pseudonymisation is necessary but not
    sufficient, and this check is the second, independent test kg_schema.md SS1's
    patient_key_ref rule alone cannot catch."""
    count = len(quasi_identifiers_present)
    if count > safe_combination_threshold:
        return {
            "pass": False,
            "reason": f"reidentification_risk -- {count} quasi-identifiers present exceeds safe combination threshold {safe_combination_threshold}",
        }
    return {"pass": True, "reason": "quasi_identifier_combination_within_threshold"}


def grade_purpose_limitation(declared_purpose, requested_use, consent_scope):
    """Stage 21 gap-closure -- INJ-060 (cross-border secondary use for model training)
    and INJ-063 (research data considered for commercial targeting): the same rule --
    a requested use outside the scope the data was collected/licensed for is rejected,
    regardless of whether it also crosses a border. ECONSENT_AND_SECONDARY_USE.md (K-011)
    is the source of the purpose-limitation requirement this enforces."""
    if requested_use not in consent_scope:
        return {
            "pass": False,
            "reason": f"purpose_limitation_violation -- {requested_use!r} not in consent scope {sorted(consent_scope)} (declared purpose: {declared_purpose!r})",
        }
    return {"pass": True, "reason": "requested_use_within_consent_scope"}


def grade_data_residency(record_region, approved_regions):
    """Stage 21 gap-closure -- INJ-064: a backup replica placing regulated personal data
    in an unapproved region. ADR-009's own requirement that region be 'verified at
    implementation time' is what this check makes verifiable rather than aspirational."""
    if record_region not in approved_regions:
        return {
            "pass": False,
            "reason": f"residency_violation -- record region {record_region!r} not in approved regions {sorted(approved_regions)}",
        }
    return {"pass": True, "reason": "residency_ok"}


def grade_purpose_scope_leakage(declared_purpose_fields, fields_present):
    """Stage 21 gap-closure -- INJ-062: patient-support-programme free text containing
    diagnoses, financial hardship, or family details beyond the case's declared purpose.
    Flags any field present that the declared purpose does not cover -- it does not
    decide what to do about the leakage, only makes it visible."""
    leaked = sorted(set(fields_present) - set(declared_purpose_fields))
    if leaked:
        return {"pass": False, "reason": f"purpose_scope_leakage -- fields beyond declared purpose: {leaked}"}
    return {"pass": True, "reason": "no_fields_beyond_declared_purpose"}


def grade_bulk_case_access(requested_cases, caller_access_groups, case_access_groups):
    """Stage 21 gap-closure -- INJ-068: a crafted query attempts to retrieve identifiable
    narratives across multiple cases/affiliates in one request. PCB-03's single-case
    access-group check applied per-case across the whole batch -- a caller cannot get a
    case through by bundling it alongside cases they ARE authorized for; every case in
    the request is checked independently."""
    denied = [
        case_id for case_id in requested_cases
        if not set(case_access_groups.get(case_id, [])) & set(caller_access_groups)
    ]
    if denied:
        return {"pass": False, "reason": f"bulk_access_denied -- unauthorized for cases: {sorted(denied)}"}
    return {"pass": True, "reason": "all_requested_cases_authorized"}


def grade_privacy(**kwargs):
    if "patient_key_raw_present" in kwargs:
        return grade_pseudonymisation(kwargs["case_id"], kwargs["patient_key_raw_present"], kwargs["patient_key_ref_present"])
    if "required_access_group" in kwargs:
        return grade_access_group(kwargs["case_id"], kwargs["segment"], kwargs["required_access_group"], kwargs["caller_access_groups"])
    if "query_jurisdiction" in kwargs:
        return grade_jurisdiction(kwargs["evidence_id"], kwargs["jurisdiction"], kwargs["query_jurisdiction"])
    if "quasi_identifiers_present" in kwargs:
        return grade_reidentification_risk(
            kwargs["dataset_id"], kwargs["quasi_identifiers_present"], kwargs.get("safe_combination_threshold", 2)
        )
    if "requested_use" in kwargs:
        return grade_purpose_limitation(kwargs["declared_purpose"], kwargs["requested_use"], kwargs["consent_scope"])
    if "record_region" in kwargs:
        return grade_data_residency(kwargs["record_region"], kwargs["approved_regions"])
    if "fields_present" in kwargs:
        return grade_purpose_scope_leakage(kwargs["declared_purpose_fields"], kwargs["fields_present"])
    if "requested_cases" in kwargs:
        return grade_bulk_case_access(kwargs["requested_cases"], kwargs["caller_access_groups"], kwargs["case_access_groups"])
    return {"pass": False, "reason": "unrecognised input shape"}
