"""supply.generate_options -- implements
packages/contracts/tool_contracts/supply_generate_options.schema.json exactly, over the
synthetic supply fixtures (tests/fixtures/synthetic/supply/*.json). Stage 20b's minimal
real-data substitute for V1's cross-repo supply/inventory data (NAB-3).

The constraint filter is applied BEFORE this tool returns -- the agent ranks within the
result, it cannot widen the set (agent_roster.md SS2). In this fixture-backed
implementation the "filter" is simply which fixture file exists for a product_id; a real
deployment would apply constraint_set against live inventory data here.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "synthetic" / "supply"


class ToolError(Exception):
    def __init__(self, code: str, meaning: str):
        self.code = code
        self.meaning = meaning
        super().__init__(f"{code}: {meaning}")


def _load_fixture(product_id: str) -> dict:
    path = FIXTURES_DIR / f"{product_id}.json"
    if not path.exists():
        raise ToolError("INVENTORY_SNAPSHOT_UNAVAILABLE", f"No fixture for product_id {product_id!r}.")
    return json.loads(path.read_text())


def generate_options(run_id: str, product_id: str, constraint_set: dict, evidence_ids: list[str]) -> dict:
    """Matches supply_generate_options.schema.json's input/output shape exactly."""
    if not run_id or not product_id or not evidence_ids:
        raise ToolError("INVENTORY_SNAPSHOT_UNAVAILABLE", "Missing required input fields.")

    start = time.monotonic()
    fixture = _load_fixture(product_id)
    latency_ms = int((time.monotonic() - start) * 1000)

    if not fixture["options"]:
        raise ToolError(
            "CONSTRAINT_SET_EMPTY_RESULT",
            f"No option satisfies the constraint set for {product_id!r}.",
        )

    return {
        "options": fixture["options"],
        "inventory_snapshot_version": fixture["inventory_snapshot_version"],
        "tool_accounting": {"latency_ms": latency_ms},
        # Stage 21 gap-closure (INJ-056) -- informational triage flags only, sourced
        # straight from the fixture with a safe empty default.
        "allocation_ethics_flags": fixture.get("allocation_ethics_flags", []),
    }
