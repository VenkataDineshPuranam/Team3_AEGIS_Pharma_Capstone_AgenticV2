"""ADR-008/ADR-010: only batch_review may import or call precedent tools."""
from datetime import date
from pathlib import Path

from packages.domain.evidence import EvidenceItem
from packages.domain.payloads import BatchPayload, ReconciliationFinding
from packages.domain.state import DecisionSupportOutput, new_state
from services.api.nodes.llm_interface import StubLLM

REPO_ROOT = Path(__file__).resolve().parents[2]
API_DIR = REPO_ROOT / "services" / "api"
GRAPH_FILES = (
    "pv_graph.py",
    "supply_graph.py",
    "research_graph.py",
    "clinical_graph.py",
    "regulatory_graph.py",
)


def test_non_batch_graphs_do_not_import_precedent():
    for name in GRAPH_FILES:
        source = (API_DIR / name).read_text(encoding="utf-8")
        assert "precedent_retrieve" not in source
        assert "precedent_mint" not in source
        assert "precedent.retrieve" not in source


def test_stub_llm_with_precedent_does_not_skip_hitl_or_emit_disposition():
    """A cited HP-* item is a fact. StubLLM still produces DecisionSupportOutput;
    there is no path that marks the run completed without HITL."""
    state = new_state(run_id="R-hp", workflow="batch_review", requester_role="EU Qualified Person")
    state["domain_payload"] = BatchPayload(
        batch_id="B-002",
        reconciliation_complete=False,
        findings=(
            ReconciliationFinding(category="genealogy", status="gap", evidence_ids=("K-006",), gap_description="missing"),
        ),
    )
    state["evidence"] = [
        EvidenceItem(evidence_id="K-006", source="SOP.md", status="approved", effective_date=date(2024, 1, 1)),
        EvidenceItem(
            evidence_id="HP-R-prior",
            source="human_precedent/R-prior.md",
            status="draft",
            effective_date=date(2026, 8, 1),
            content_excerpt="Genealogy incomplete.",
        ),
    ]
    draft, _, _ = StubLLM().synthesize(state)
    assert isinstance(draft, DecisionSupportOutput)
    dumped = draft.model_dump()
    assert "release_recommended" not in dumped
    assert "reject_recommended" not in dumped
    assert "auto_approved" not in dumped
    assert any(c.cites == ("HP-R-prior",) or "HP-R-prior" in c.cites for c in draft.claims)
    assert "reject the batch" not in draft.summary.lower()
    for claim in draft.claims:
        assert "reject the batch" not in claim.text.lower()

    import inspect

    import services.api.graph as graph_module

    source = inspect.getsource(graph_module.build_graph)
    assert 'graph.add_edge("precedent_retrieve", "synthesize")' in source
    assert '"degraded": "finalize", "guard1": "guard1"' in source
