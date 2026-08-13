"""prohibited_action_guard -- Stage 20a Phase 3. ADR-004 layer 3 (runtime guard), the
third of three independent enforcement layers. Layer 1 (schema absence) and layer 2 (tool
capability absence) are already structurally enforced by packages/domain/payloads.py's
`extra="forbid"` models and the tool_contracts JSON schemas -- this module is what runs
against generated TEXT, which those layers cannot see.

Invoked twice per graph (guard1 before Critic, guard2 after -- hooks.md, langgraph_design.md
"why the guard runs twice"). One implementation, called from both places -- not duplicated.

Pattern-matches output shape; does not ask the model whether its own output is acceptable
(hooks.md's own invariant for this row).
"""
from __future__ import annotations

from dataclasses import dataclass

from packages.domain.state import DecisionSupportOutput, ProhibitionContract


@dataclass(frozen=True)
class GuardResult:
    verdict: str  # "clear" | "blocked"
    matched_terms: tuple[str, ...] = ()


def check(draft: DecisionSupportOutput, contract: ProhibitionContract) -> GuardResult:
    text = draft.summary + " " + " ".join(c.text for c in draft.claims)
    text_lower = text.lower()

    matched = tuple(term for term in contract.banned_terms if term.lower() in text_lower)

    # Defense-in-depth: banned_field_names should be structurally unreachable (layer 1),
    # but checked here too so a guard failure is never the only thing standing between a
    # malformed node and a disposition field reaching a caller.
    dumped = draft.model_dump()
    field_hits = tuple(name for name in contract.banned_field_names if name in dumped)

    if matched or field_hits:
        return GuardResult(verdict="blocked", matched_terms=matched + field_hits)
    return GuardResult(verdict="clear")
