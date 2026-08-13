# DMAIC Lens — Stage 11 (MCP)

**Thin lens** (per `prompts/15_mcp.md`). Governed by `docs/quality/dmaic-lean/` — the
consolidated registers, not a restart.

## Define

Which tool-layer decisions exist specifically to remove a named waste, and which the prompt's
own Lean questions ask for directly.

## Measure

| Metric | Value | Note |
|---|---|---|
| Distinct tool operations | 7 | Across 6 server registrations |
| Tools that are read-only | **7 of 7** | See `prohibited_write_enforcement.md` §1 |
| Tools with a `contract_version` | 7 of 7 | BC-10 |
| Tools cacheable without further design | 2 of 7 (`evidence.retrieve`, `pv.normalize_terminology`) | §Analyze below |
| Tools explicitly marked do-not-cache | 1 of 7 (`supply.generate_options`) | New finding this stage |
| `.claude/mcp.json` live server entries | **0** | Deliberate — see `tool_inventory.md` §8 |

## Analyze

**Which tool contracts prevent Integration waste (agents guessing at undocumented APIs)?**
All seven — every input/output shape, error code, and idempotency key is written down before
any code exists, which is the point of doing this stage before Stage 20. The specific
mechanism that goes further than "documented": `evidence.retrieve`'s scope is not a
documented convention the agent must get right, it is **absent from the schema entirely**
(§1 of `tool_inventory.md`) — the strongest form of preventing Integration waste is removing
the parameter an agent could get wrong, not documenting the correct value.

**Which tool calls are cacheable vs. must never be cached?** This is the direct handoff to
Stage 18. The finding worth stating plainly: **the two easy answers (retrieval is cacheable,
writes aren't) don't cover the real risk.** All seven tools are read-only, so "read-only
implies cacheable" would be the naive conclusion — and it's wrong for two of them:

- `pv.duplicate_check` is read-only but **time-dependent on data the tool doesn't own** — a
  case that wasn't a duplicate an hour ago can become one as new cases arrive. Caching it like
  a pure retrieval would silently reintroduce the D5/stale-inventory waste (register row) in a
  place the naive read/write split would have missed entirely.
- `supply.generate_options` is read-only but depends on the **most volatile data in the
  system** (inventory, quality status). A cached option set doesn't just risk being stale
  evidence — it risks recommending against inventory that no longer exists, which is an
  operational failure mode this programme hasn't had to name before, one level past D5's
  evidentiary staleness.

Neither of these was visible from "is it read-only." Both are visible from "what does the
result depend on, and how fast does that change."

## Improve

The tool inventory and contracts are the Improve artifact. What they implement from
`build_constraints_from_lean.md`: **BC-2** (status filter inside the tool, before ranking —
enforced here by removing the caller-supplied `scope` field, a stronger form than the
constraint asked for), **BC-10** (versioned schemas; `tests/contract/` still to be populated at
Stage 20, named as an open dependency), and the AI-Integration register row directly (tool
contract tests prevent silent drift, once they exist).

**A design choice this stage made that the prior stages did not specify:** one MCP server per
bounded context for evidence retrieval, rather than one server with a scope parameter
(`tool_inventory.md` §1). This wasn't required by any prior artifact — it's this stage applying
ADR-004's own argument ("don't rely on the caller passing the right value") one layer down,
to tools rather than to domain aggregates. Recorded here because it's a design decision, not
just an implementation of one.

## Control

**Revisit triggers added by this stage:**

- If Stage 15 needs `pv.duplicate_check` or `supply.generate_options` cached for cost reasons,
  the invalidation design (case-ingestion event for PV; inventory-snapshot-version check for
  Supply) must exist **before** caching is turned on, not after — same ordering principle as
  Redis being excluded from 20a until correctness is proven.
- If any tool contract gains a field matching `what_this_schema_cannot_express`, that is not a
  schema change — it requires a new ADR (`prohibited_write_enforcement.md` §5).
- `tests/contract/` does not exist yet. Its absence is not a defect at this stage (no code
  exists to test), but Stage 20 cannot claim BC-10 satisfied without it existing and passing.
