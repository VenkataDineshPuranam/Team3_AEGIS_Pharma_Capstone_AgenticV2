"""LLM node interface -- Stage 20a Phase 4/5.

Two methods, `synthesize` and `critic`, implemented by:
  - StubLLM (this file): deterministic fake responses, no network call. Used by Phase 4's
    graph-shape tests so routing/caps/guards can be exercised with zero API key.
  - packages/config/llm_client.py's real clients (Phase 5): Grok (dev-only, provisional
    results) and Anthropic (Route A, ADR-009 -- the only provider whose output counts
    toward Stage 20a's interim-assumption exit criteria).

Swapping which one `services/api/graph.py` uses is a constructor argument, never a graph
change -- this is the interface ADR-009's "one client interface" guardrail exists for.
"""
from __future__ import annotations

from typing import Protocol

from packages.domain.evidence import Claim
from packages.domain.state import DecisionSupportOutput, GovernedState, ReasonCode


class LLMNodes(Protocol):
    def synthesize(self, state: GovernedState) -> tuple[DecisionSupportOutput, int, int]:
        """Returns (draft_output, tokens_in, tokens_out)."""
        ...

    def critic(self, state: GovernedState) -> tuple[str, ReasonCode | None, int, int]:
        """Returns (verdict, reason_code, tokens_in, tokens_out).
        verdict: 'approve_for_human' | 'reject'."""
        ...


class StubLLM:
    """No network call. Reads domain_payload's findings and produces a deterministic
    draft that cites real evidence_ids -- enough for guard/critic/HITL routing to be
    exercised meaningfully without a model."""

    def synthesize(self, state: GovernedState) -> tuple[DecisionSupportOutput, int, int]:
        payload = state["domain_payload"]
        gaps = [f for f in payload.findings if f.status != "complete"]
        evidence_ids = tuple(e.evidence_id for e in state["evidence"])
        if gaps:
            summary = f"Batch {payload.batch_id}: {len(gaps)} category/categories not complete."
            claims = tuple(
                Claim(text=f"{g.category}: {g.status} -- {g.gap_description or 'no description'}", cites=evidence_ids)
                for g in gaps
            )
        else:
            summary = f"Batch {payload.batch_id}: all reconciliation categories complete."
            claims = (Claim(text="All categories complete per retrieved evidence.", cites=evidence_ids),)
        draft = DecisionSupportOutput(summary=summary, claims=claims)
        return draft, 100, 50

    def critic(self, state: GovernedState) -> tuple[str, ReasonCode | None, int, int]:
        draft = state["draft_output"]
        for claim in draft.claims:
            if not claim.cites:
                return "reject", ReasonCode.MISSING_CITATION, 80, 20
        return "approve_for_human", None, 80, 20
