"""evidence_gate -- Stage 20a Phase 3. ADR-003: status lookup, never interpretation.
A non-citable item cannot even be constructed as an EvidenceItem (packages/domain/evidence.py's
CitableStatus Literal only permits approved/draft) -- this module is the SECOND independent
check the langgraph_design.md design calls for, over the retrieved list as a whole rather
than per-item construction, catching the class of bug where a filtered-wrong list still
type-checks (e.g. an empty list mistaken for 'sufficient').
"""
from __future__ import annotations

from dataclasses import dataclass

from packages.domain.evidence import EvidenceItem

# G3: failure_and_loop_guards.md -- one scope-preserving broadening permitted, then abstain.
_MAX_BROADENINGS = 1


@dataclass(frozen=True)
class GateResult:
    outcome: str  # "sufficient" | "broaden" | "abstain" | "defect_halt"
    reason: str = ""


def check(evidence: list[EvidenceItem], broadenings_used: int) -> GateResult:
    # Structural guarantee from packages/domain/evidence.py: every item in this list has
    # status in {"approved", "draft"} by construction. This assertion documents that
    # guarantee at the point it matters, rather than leaving it implicit.
    non_citable = [e for e in evidence if e.status not in ("approved", "draft")]
    if non_citable:
        # Should be unreachable given the type constraint -- if this ever fires, the
        # ADR-003 filter failed upstream and the run is untrustworthy (gate_defect).
        return GateResult(outcome="defect_halt", reason="non-citable item present despite type constraint")

    if evidence:
        return GateResult(outcome="sufficient")

    if broadenings_used < _MAX_BROADENINGS:
        return GateResult(outcome="broaden")

    return GateResult(outcome="abstain", reason="insufficient_evidence")
