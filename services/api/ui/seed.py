"""Idempotent synthetic dockets so the workbench is information-complete without an LLM key.

Live graph runs (POST /api/runs) are unchanged. These rows are marked demo_seed=True
so decide can close them locally when the checkpointer has no thread.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from services.api import pending_queue, run_snapshots

K006 = {
    "evidence_id": "K-006",
    "source": "BATCH_RELEASE_EVIDENCE_POLICY.md",
    "status": "approved",
    "effective_date": "2026-06-01",
    "jurisdiction": "Global",
    "supersedes": "K-007",
    "content_excerpt": (
        "An evidence pack is structurally complete only when genealogy, laboratory, "
        "environmental monitoring, deviation, CAPA, change-control, validation, supplier, "
        "and packet-completeness findings are each cited. Completeness is not a release, "
        "rejection, reprocess, relabel, or recall decision."
    ),
}
K007 = {
    "evidence_id": "K-007",
    "source": "BATCH_RELEASE_POLICY_OLD.md",
    "status": "superseded",
    "effective_date": "2024-01-01",
    "jurisdiction": "Global",
    "supersedes": None,
    "content_excerpt": (
        "Superseded 2024 policy. Cited only to show both sources when a conflict exists. "
        "Must not be used as the current control."
    ),
}
K003 = {
    "evidence_id": "K-003",
    "source": "AI_GXP_BOUNDARY.md",
    "status": "approved",
    "effective_date": "2026-05-01",
    "jurisdiction": "Global",
    "supersedes": None,
    "content_excerpt": (
        "Agents produce decision support. No model output may be treated as a terminal "
        "GxP action. Silence is not approval."
    ),
}
K009 = {
    "evidence_id": "K-009",
    "source": "COLD_CHAIN_ASSESSMENT.md",
    "status": "approved",
    "effective_date": "2026-04-30",
    "jurisdiction": "Global",
    "supersedes": None,
    "content_excerpt": (
        "Cold-chain lanes are described as evidence of constraint satisfaction. "
        "Description of a lane is not authorization to ship or allocate."
    ),
}


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat()


def _cases(now: datetime) -> list[dict]:
    t_batch = now - timedelta(hours=6)
    t_pv = now - timedelta(hours=3)
    t_supply = now - timedelta(hours=2)
    t_done = now - timedelta(hours=18)
    t_block = now - timedelta(hours=10)
    t_to = now - timedelta(hours=26)

    batch_findings = [
        {
            "category": "genealogy",
            "status": "gap",
            "evidence_ids": ["K-006"],
            "gap_description": (
                "Material lot ML-9931 consumed_by B-002 has no traceable genealogy record "
                "(missing_branch). Absence is the finding."
            ),
        },
        {"category": "lab_results", "status": "complete", "evidence_ids": ["K-006"], "gap_description": None},
        {
            "category": "environmental_monitoring",
            "status": "complete",
            "evidence_ids": ["K-006"],
            "gap_description": None,
        },
        {"category": "deviations", "status": "complete", "evidence_ids": ["K-006"], "gap_description": None},
        {"category": "capa", "status": "complete", "evidence_ids": ["K-006"], "gap_description": None},
        {"category": "change_control", "status": "complete", "evidence_ids": ["K-006"], "gap_description": None},
        {"category": "validation_state", "status": "complete", "evidence_ids": ["K-006"], "gap_description": None},
        {"category": "supplier_evidence", "status": "complete", "evidence_ids": ["K-006"], "gap_description": None},
        {
            "category": "release_packet_completeness",
            "status": "gap",
            "evidence_ids": ["K-006", "K-003"],
            "gap_description": "Packet cannot be marked complete while genealogy is unresolved.",
        },
    ]

    return [
        {
            "run_id": "R-WB-B002",
            "workflow": "batch_review",
            "subject_id": "B-002",
            "requester_role": "Manufacturing VP",
            "status": "pending_approval",
            "terminal_state": None,
            "abstention_reason": None,
            "llm_calls": 2,
            "tool_calls": 4,
            "tokens_in": 1840,
            "tokens_out": 612,
            "draft_summary": (
                "Reconciliation for synthetic batch B-002 (Site-EU-01, manufacture 2026-06-01) "
                "is incomplete. Genealogy for consumed lot ML-9931 is absent; eight other "
                "categories are cited complete against K-006. Release-packet completeness is "
                "therefore also a gap. This summary records structural status only."
            ),
            "draft_claims": [
                {
                    "text": "Genealogy for lot ML-9931 is not present in the retrieved graph.",
                    "cites": ["K-006"],
                },
                {
                    "text": "Lab, EM, deviation, CAPA, change-control, validation, and supplier findings are cited complete.",
                    "cites": ["K-006"],
                },
                {
                    "text": "Packet completeness remains a gap while genealogy is unresolved.",
                    "cites": ["K-006", "K-003"],
                },
            ],
            "approver_roles": ["EU Qualified Person", "Chief Quality Officer"],
            "required_legs": None,
            "approved_legs": [],
            "policy_contract_version": "v1",
            "hitl_status": "awaiting_human",
            "hitl_tier": "T0",
            "hitl_deadline": _iso(t_batch + timedelta(hours=8)),
            "veto_recorded": False,
            "evidence": [K006, K003, K007],
            "domain_payload": {
                "batch_id": "B-002",
                "reconciliation_complete": False,
                "findings": batch_findings,
            },
            "critic_verdict": "approve_for_human",
            "critic_reason_codes": [],
            "guard_verdict": "pass",
            "trace_id": "tr-wb-b002",
            "created_at": _iso(t_batch),
            "demo_seed": True,
        },
        {
            "run_id": "R-WB-PV002",
            "workflow": "pv_intake",
            "subject_id": "PV-002",
            "requester_role": "Global Head of Pharmacovigilance",
            "status": "pending_approval",
            "terminal_state": None,
            "abstention_reason": None,
            "llm_calls": 2,
            "tool_calls": 3,
            "tokens_in": 1210,
            "tokens_out": 440,
            "draft_summary": (
                "Case PV-002 is a triage pack only. Duplicate check against window cw-2026-08-13 "
                "returned candidate PV-001 (similarity 0.87 on patient identifiers, product, and "
                "event date). Terminology suggestion: nausea (MedDRA v27.0). No seriousness, "
                "causality, expectedness, or reportability determination is included."
            ),
            "draft_claims": [
                {
                    "text": "Duplicate-suspicion flag is set after comparison with PV-001.",
                    "cites": ["K-003"],
                },
                {
                    "text": "Source text maps to suggested MedDRA term nausea; suggestion is not applied.",
                    "cites": ["K-003"],
                },
            ],
            "approver_roles": ["Global Head of Pharmacovigilance", "Chief Medical Officer"],
            "required_legs": None,
            "approved_legs": [],
            "policy_contract_version": "v1",
            "hitl_status": "awaiting_human",
            "hitl_tier": "T0",
            "hitl_deadline": _iso(t_pv + timedelta(hours=4)),
            "veto_recorded": False,
            "evidence": [K003],
            "domain_payload": {
                "case_id": "PV-002",
                "duplicate_suspected": True,
                "comparison_window_version": "cw-2026-08-13",
                "candidates": [
                    {
                        "candidate_case_id": "PV-001",
                        "similarity_score": 0.87,
                        "matched_fields": ["patient_identifiers", "product", "event_date"],
                    }
                ],
                "normalization_suggestions": [
                    {
                        "normalized_term": "nausea",
                        "confidence": 0.96,
                        "terminology_source": "MedDRA v27.0",
                    }
                ],
                "terminology_table_version": "meddra-27.0",
                "source_text": "same patient, dose reaction, nausea reported twice this week",
            },
            "critic_verdict": "approve_for_human",
            "critic_reason_codes": [],
            "guard_verdict": "pass",
            "trace_id": "tr-wb-pv002",
            "created_at": _iso(t_pv),
            "demo_seed": True,
        },
        {
            "run_id": "R-WB-P100",
            "workflow": "supply_planning",
            "subject_id": "P-100",
            "requester_role": "Supply Chain VP",
            "status": "pending_approval",
            "terminal_state": None,
            "abstention_reason": None,
            "llm_calls": 2,
            "tool_calls": 3,
            "tokens_in": 1560,
            "tokens_out": 505,
            "draft_summary": (
                "Two constraint-filtered options exist for product P-100 against inventory "
                "snapshot snap-2026-08-13. Planning leg is recorded. Quality leg is still open. "
                "Neither option is an allocation, reservation, or shipment."
            ),
            "draft_claims": [
                {
                    "text": "OPT-1 stays inside EU-West market authorization and CMO-B capacity window.",
                    "cites": ["K-009"],
                },
                {
                    "text": "OPT-2 uses in-market buffer; no transport change is described.",
                    "cites": ["K-009"],
                },
            ],
            "approver_roles": ["Supply Chain VP", "EU Qualified Person", "Chief Quality Officer"],
            "required_legs": ["planning", "quality"],
            "approved_legs": ["planning"],
            "policy_contract_version": "v1",
            "hitl_status": "awaiting_human",
            "hitl_tier": "T0",
            "hitl_deadline": _iso(t_supply + timedelta(hours=8)),
            "veto_recorded": False,
            "evidence": [K009, K003],
            "domain_payload": {
                "product_id": "P-100",
                "inventory_snapshot_version": "snap-2026-08-13",
                "constraint_set": {
                    "market_authorization_scope": ["EU-West"],
                    "cold_chain_requirements": ["2-8C"],
                    "trial_demand_reservations": [],
                    "compassionate_use_constraints": [],
                    "cmo_capacity_window": "2026-W33",
                },
                "options": [
                    {
                        "option_id": "OPT-1",
                        "description": "Redirect CMO-B capacity within existing market authorization for region EU-West.",
                        "constraints_satisfied": ["market_authorization_scope", "cmo_capacity_window"],
                        "cold_chain_evidence_ids": ["K-009"],
                        "transport_notes": "Standard cold-chain lane, no exception required.",
                    },
                    {
                        "option_id": "OPT-2",
                        "description": "Draw down existing EU-West inventory buffer ahead of scheduled replenishment.",
                        "constraints_satisfied": ["market_authorization_scope"],
                        "cold_chain_evidence_ids": ["K-009"],
                        "transport_notes": "No transport change required; buffer is already in-market.",
                    },
                ],
            },
            "critic_verdict": "approve_for_human",
            "critic_reason_codes": [],
            "guard_verdict": "pass",
            "trace_id": "tr-wb-p100",
            "created_at": _iso(t_supply),
            "demo_seed": True,
        },
        {
            "run_id": "R-WB-B001",
            "workflow": "batch_review",
            "subject_id": "B-001",
            "requester_role": "EU Qualified Person",
            "status": "completed",
            "terminal_state": "completed",
            "abstention_reason": None,
            "llm_calls": 2,
            "tool_calls": 3,
            "tokens_in": 980,
            "tokens_out": 310,
            "draft_summary": (
                "Reconciliation for synthetic batch B-001 lists all nine categories complete "
                "against K-006. Human accepted the evidence pack. That is not a batch release."
            ),
            "draft_claims": [
                {"text": "All nine reconciliation categories are cited complete.", "cites": ["K-006"]},
            ],
            "approver_roles": ["EU Qualified Person", "Chief Quality Officer"],
            "required_legs": None,
            "approved_legs": [],
            "policy_contract_version": "v1",
            "hitl_status": "resolved",
            "hitl_tier": None,
            "hitl_deadline": None,
            "veto_recorded": False,
            "evidence": [K006],
            "domain_payload": {
                "batch_id": "B-001",
                "reconciliation_complete": True,
                "findings": [
                    {"category": c, "status": "complete", "evidence_ids": ["K-006"], "gap_description": None}
                    for c in [
                        "genealogy",
                        "lab_results",
                        "environmental_monitoring",
                        "deviations",
                        "capa",
                        "change_control",
                        "validation_state",
                        "supplier_evidence",
                        "release_packet_completeness",
                    ]
                ],
            },
            "critic_verdict": "approve_for_human",
            "critic_reason_codes": [],
            "guard_verdict": "pass",
            "trace_id": "tr-wb-b001",
            "created_at": _iso(t_done),
            "audit_events": [
                {
                    "kind": "HumanOverrideRecorded",
                    "action": "approved",
                    "justification": "Evidence pack accepted; genealogy and packet are complete on K-006.",
                    "recorded_at": _iso(t_done + timedelta(hours=1)),
                    "actor_role": "EU Qualified Person",
                },
                {
                    "kind": "AgentRun",
                    "terminal_state": "completed",
                    "recorded_at": _iso(t_done + timedelta(hours=1)),
                    "policy_contract_version": "v1",
                },
            ],
            "demo_seed": True,
        },
        {
            "run_id": "R-WB-BLOCK",
            "workflow": "batch_review",
            "subject_id": "B-003",
            "requester_role": "Manufacturing VP",
            "status": "blocked",
            "terminal_state": "blocked",
            "abstention_reason": "prohibited_action",
            "llm_calls": 1,
            "tool_calls": 2,
            "tokens_in": 640,
            "tokens_out": 180,
            "draft_summary": None,
            "draft_claims": [],
            "approver_roles": ["EU Qualified Person"],
            "required_legs": None,
            "approved_legs": [],
            "policy_contract_version": "v1",
            "hitl_status": "blocked",
            "hitl_tier": None,
            "hitl_deadline": None,
            "veto_recorded": False,
            "evidence": [K003],
            "domain_payload": {"batch_id": "B-003", "reconciliation_complete": False, "findings": []},
            "critic_verdict": None,
            "critic_reason_codes": ["PROHIBITION_ADJACENT"],
            "guard_verdict": "blocked",
            "trace_id": "tr-wb-block",
            "created_at": _iso(t_block),
            "audit_events": [
                {
                    "kind": "ProhibitedActionBlocked",
                    "matched_terms": ["release"],
                    "draft_sha256": "a3f1c8e0demo",
                    "recorded_at": _iso(t_block),
                }
            ],
            "demo_seed": True,
        },
        {
            "run_id": "R-WB-T3",
            "workflow": "pv_intake",
            "subject_id": "PV-001",
            "requester_role": "Global Head of Pharmacovigilance",
            "status": "timed_out",
            "terminal_state": "abstained",
            "abstention_reason": "hitl_timeout",
            "llm_calls": 2,
            "tool_calls": 2,
            "tokens_in": 800,
            "tokens_out": 220,
            "draft_summary": (
                "Triage pack for PV-001 reached T3 with no human action. No decision was made; resubmit."
            ),
            "draft_claims": [
                {"text": "No duplicate candidates in window cw-2026-08-13.", "cites": ["K-003"]},
            ],
            "approver_roles": ["Global Head of Pharmacovigilance"],
            "required_legs": None,
            "approved_legs": [],
            "policy_contract_version": "v1",
            "hitl_status": "expired",
            "hitl_tier": "T3",
            "hitl_deadline": _iso(t_to + timedelta(hours=24)),
            "veto_recorded": False,
            "evidence": [K003],
            "domain_payload": {
                "case_id": "PV-001",
                "duplicate_suspected": False,
                "comparison_window_version": "cw-2026-08-13",
                "candidates": [],
                "normalization_suggestions": [
                    {
                        "normalized_term": "nausea",
                        "confidence": 0.94,
                        "terminology_source": "MedDRA v27.0",
                    }
                ],
                "terminology_table_version": "meddra-27.0",
            },
            "critic_verdict": "approve_for_human",
            "critic_reason_codes": [],
            "guard_verdict": "pass",
            "trace_id": "tr-wb-t3",
            "created_at": _iso(t_to),
            "audit_events": [
                {
                    "kind": "HitlExpired",
                    "abstention_reason": "hitl_timeout",
                    "recorded_at": _iso(t_to + timedelta(hours=24)),
                    "message": "No decision was made; resubmit.",
                }
            ],
            "demo_seed": True,
        },
    ]


def ensure() -> None:
    now = datetime.now(UTC)
    for snap in _cases(now):
        if run_snapshots.get(snap["run_id"]) is not None:
            continue
        run_snapshots.upsert(snap)
        if snap["status"] == "pending_approval":
            pending_queue.add(
                pending_queue.PendingEntry(
                    run_id=snap["run_id"],
                    workflow=snap["workflow"],
                    subject_id=snap["subject_id"],
                    requester_role=snap["requester_role"],
                    approver_roles=snap["approver_roles"],
                    required_legs=snap.get("required_legs"),
                    approved_legs=snap.get("approved_legs") or [],
                    draft_summary=snap.get("draft_summary"),
                    draft_claims=snap.get("draft_claims") or [],
                    created_at=snap["created_at"],
                    snapshot=snap,
                )
            )


def apply_demo_decision(
    snap: dict,
    *,
    action: str,
    justification: str,
    leg: str | None,
    actor_role: str,
) -> dict:
    snap = dict(snap)
    now = datetime.now(UTC).isoformat()
    events = list(snap.get("audit_events") or [])
    if snap.get("workflow") == "supply_planning" and action in ("approved", "rejected") and leg:
        if action == "rejected":
            snap["status"] = "abstained"
            snap["terminal_state"] = "abstained"
            snap["hitl_status"] = "resolved"
            pending_queue.remove(snap["run_id"])
        else:
            legs = list(snap.get("approved_legs") or [])
            if leg not in legs:
                legs.append(leg)
            snap["approved_legs"] = legs
            required = list(snap.get("required_legs") or ["planning", "quality"])
            if set(required).issubset(set(legs)):
                snap["status"] = "completed"
                snap["terminal_state"] = "completed"
                snap["hitl_status"] = "resolved"
                pending_queue.remove(snap["run_id"])
            else:
                snap["status"] = "pending_approval"
                pending_queue.update_snapshot(snap["run_id"], snap)
        events.append(
            {
                "kind": "HumanOverrideRecorded",
                "action": action,
                "leg": leg,
                "justification": justification,
                "recorded_at": now,
                "actor_role": actor_role,
            }
        )
    elif action == "veto":
        snap["status"] = "abstained"
        snap["terminal_state"] = "abstained"
        snap["veto_recorded"] = True
        snap["hitl_status"] = "vetoed"
        pending_queue.remove(snap["run_id"])
        events.append(
            {
                "kind": "HumanOverrideRecorded",
                "action": "veto",
                "justification": justification,
                "recorded_at": now,
                "actor_role": actor_role,
            }
        )
    elif action == "approved":
        snap["status"] = "completed"
        snap["terminal_state"] = "completed"
        snap["hitl_status"] = "resolved"
        pending_queue.remove(snap["run_id"])
        events.append(
            {
                "kind": "HumanOverrideRecorded",
                "action": "approved",
                "justification": justification,
                "recorded_at": now,
                "actor_role": actor_role,
            }
        )
    else:
        snap["status"] = "abstained"
        snap["terminal_state"] = "abstained"
        snap["hitl_status"] = "resolved"
        pending_queue.remove(snap["run_id"])
        events.append(
            {
                "kind": "HumanOverrideRecorded",
                "action": action,
                "justification": justification,
                "recorded_at": now,
                "actor_role": actor_role,
            }
        )
    snap["audit_events"] = events
    run_snapshots.upsert(snap)
    return snap
