"""policy_load -- Stage 20a Phase 3. Executes langgraph_design.md node #2: loads the
versioned policy contract; REFUSES if unreachable, no cached-policy fallback (ADR-005,
BC-3, P-05 in docs/governance/policy_register.md).

This is the one governance module every other Phase-3 module depends on -- if this
raises, the graph must route to `refuse`, never proceed on a stale or default contract.
"""
from __future__ import annotations

import json
from pathlib import Path

from packages.domain.state import ProhibitionContract, Workflow

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = REPO_ROOT / "security" / "policies"


class PolicyEngineUnavailable(Exception):
    """ADR-005: unreachable/unreadable policy -- the graph must refuse, not proceed."""


def load_policy_contract(version: str) -> dict:
    path = POLICY_DIR / f"policy_contract.{version}.json"
    if not path.exists():
        raise PolicyEngineUnavailable(f"Policy contract {version!r} not found at {path}.")
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise PolicyEngineUnavailable(f"Policy contract {version!r} unreadable: {exc}") from exc


def get_prohibition_contract(version: str, workflow: Workflow) -> ProhibitionContract:
    contract_doc = load_policy_contract(version)
    if contract_doc.get("version") != version:
        raise PolicyEngineUnavailable(
            f"Policy file version mismatch: requested {version!r}, file declares {contract_doc.get('version')!r}."
        )
    workflow_contract = contract_doc["prohibition_contracts"].get(workflow)
    if workflow_contract is None:
        raise PolicyEngineUnavailable(f"No prohibition contract for workflow {workflow!r} in {version!r}.")
    return ProhibitionContract(**workflow_contract)
