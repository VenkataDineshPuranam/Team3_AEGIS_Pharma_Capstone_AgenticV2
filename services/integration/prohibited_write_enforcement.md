# Prohibited-Write Enforcement — Stage 11 (MCP)

**Executes:** `prompts/15_mcp.md` §3
**Builds on:** ADR-004, DDD `domain_model.md` §7/§10, C4 `c4_components.md`,
`boundary_and_degraded_mode.md`

---

## 1. The finding this document has to state plainly

**Every tool in this system's contract is read-only.** There is no write-capable tool in this
design — not "a write tool with restrictions," but zero write methods, anywhere, in any of the
seven tool contracts in `tool_contracts/`. `tool_inventory.md`'s table confirms it column by
column.

That makes this document's job different from what its name implies. There is no write path to
*enforce restrictions on*. The actual job is: **prove the absence is structural, not
incidental** — that no schema, no field, no code path in this design could grow a write method
without someone deliberately adding one, and that if someone did, a second and third layer
would still stop it. This is ADR-004's three-layer argument, applied at the tool-contract
layer specifically, which the DDD/C4 versions describe in general terms but do not walk through
tool by tool.

## 2. The three layers, applied to tools

| Layer | What it is here | Where |
|---|---|---|
| **1 — Schema absence** | No output or input field, in any of the seven contracts, is shaped like a write acknowledgment, an allocation, a release, or a disposition. `supply_generate_options.schema.json` and `batch_reconcile.schema.json` each carry an explicit `what_this_schema_cannot_express` block naming the fields that were considered and rejected | `packages/contracts/tool_contracts/*.schema.json` |
| **2 — Tool-method absence** | Each MCP server registration (`tool_inventory.md` §2) exposes exactly the tool operations listed — one JSON-RPC method per tool. There is no `supply.allocate`, `batch.release`, `pv.confirm_reportability`, or any equivalent method registered on any server, in this design or in `.claude/mcp.json`'s (currently empty) planned entries | Server registrations, §3 below |
| **3 — Runtime guard** | The Prohibited-Action Guard (`c4_components.md`, `langgraph_design.md` node `prohibited_action_guard`) inspects every state transition that produces output, independent of what any tool returned | `docs/architecture/agentic/langgraph_design.md` §1 |

**Why three layers when the tools are already read-only.** Because "the tools happen to be
read-only today" is a much weaker property than "a write cannot be added without visibly
breaking two other things." Layer 3 exists precisely for the case where layer 1 or 2 is
weakened later — a future engineer adding a field to `supply_generate_options.schema.json`
still has to pass the runtime guard, which does not trust tool output any more than it trusts
model output.

## 3. Worked example — the tool most tempting to extend with a write

`supply.generate_options` is the one contract where a write method would look like a small,
reasonable extension ("just let it reserve the option it recommends"). Walking through why that
specific temptation fails at every layer is more useful than a general statement:

1. **A developer adds `reserved_quantity` to the output schema.** This alone does nothing —
   the tool's *server implementation* still has no code path to a reservation system, because
   `services/integration/supply-planning-tools/` was never given write credentials to any
   inventory system (C4 `c4_context.md`: zero write integrations to any brownfield system,
   architecture-level, independent of this schema).
2. **A developer also wires the server to a real reservation API.** The `ShortageOption` value
   object in `domain_model.md` §7 still has no `allocated_quantity` field — the *domain*
   aggregate that the tool's output is supposed to populate cannot carry a reservation, so the
   graph has nowhere to put it even if the tool returned one.
3. **A developer also changes the domain aggregate.** The Prohibited-Action Guard's schema-level
   check (`langgraph_design.md` node `prohibited_action_guard`, sourced from
   `domain_model.md` §7's invariant list) still fires on any output resembling an allocation,
   regardless of which field it arrived in — the guard pattern-matches on *shape*, not on a
   specific field name, precisely so a rename or a new field does not evade it.

All three layers would have to be independently and knowingly defeated — a tool contract, a
domain aggregate, **and** a runtime guard's pattern set — for a single allocation write to
reach a brownfield system. That is what "structurally unrepresentable" means in practice, not
just in a design document.

## 4. The same walkthrough, one row per prohibited class

| Prohibited class | Layer 1 (schema) | Layer 2 (tool method) | Layer 3 (runtime) |
|---|---|---|---|
| Batch release / reject / reprocess / relabel / recall | `batch_reconcile.schema.json`'s `what_this_schema_cannot_express` names all five; `Batch` aggregate has no such field (DDD §7) | No `batch.release`/`batch.reject`/etc. method on `batch-review-tools/` | Guard pattern-matches disposition-shaped output before it reaches the Critic and again after (`langgraph_design.md` "why the guard runs twice") |
| PV final causality / seriousness / expectedness / reportability / signal-confirmation | `pv_duplicate_check.schema.json` output has no such fields; PV output schema (per DDD §10) structurally excludes them | No `pv.confirm_*` method exists on `pv-intake-tools/` | Same guard; **also** PV routes 100% to human regardless, so even a guard failure still requires human sign-off before anything leaves the system |
| Supply allocation / reservation / shipment / recall | `supply_generate_options.schema.json`'s `what_this_schema_cannot_express` names all four | No `supply.allocate`/`supply.reserve`/etc. method exists on `supply-planning-tools/` | Same guard; **also** Supply requires dual approval (Supply Chain VP + Quality), so no single role's approval alone can move an option toward execution |

## 5. What would actually constitute a violation of this document

Not "a tool being called with bad input" — the schemas already reject that at validation time.
The real violation classes, and what should happen if each occurs:

| Violation | Detection | Response |
|---|---|---|
| A future PR adds a write-shaped field to any tool contract | Contract test in `tests/contract/` (BC-10) asserting the negative — that these specific field names are absent — fails the build | Block the PR; require an ADR, per the note in `supply_generate_options.schema.json`'s cannot-express block |
| A tool server is registered with write credentials to a brownfield system | Architecture review (Stage 12 assurance) checking `.claude/mcp.json` / deployment config against `c4_context.md`'s zero-write-integration invariant | Stage 12 finding, release-blocking |
| The Prohibited-Action Guard's pattern set fails to catch a disposition-shaped output in testing | Stage 18 red-team, interim assumption 1 | **Stop the line** (trigger T-1) — this is not a tool-layer defect alone, it invalidates ADR-004 |

## 6. This document does not need a Stage 16 counterpart to be complete

Stage 16 (Governance & Control) will define the **policy register** and **escalation** design
in general; this document is the tool-specific instance of ADR-004 that Stage 16 inherits, not
duplicates. If Stage 16 finds a write path this document missed, that is a defect in this
document to fix, not a second enforcement mechanism to add on top.
