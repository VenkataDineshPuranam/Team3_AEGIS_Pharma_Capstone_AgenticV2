# Prompt 14 — Agentic Architecture (LangGraph Multi-Agent Design)

**Maps to:** STAGES.md Stage 10 (`stage-10-agentic-architecture`)
**Lifecycle stage:** Design (agentic runtime)
**Framework derived:** V2 addition — has no V1 equivalent (V1 was single-shot workflows, not multi-agent).
**Core question:** How do multiple agents collaborate, hand off, and stay within their authority?
**Prerequisites:** Prompt 04 DDD (agent responsibilities, §10), Prompt 06 C4 (agentic runtime view).
**Primary output type:** Agent roster + LangGraph graph design (may be provisional).

---

## Intent

Turn the DDD "agent responsibilities" and C4 "agentic runtime view" into an executable
multi-agent design: which agents exist, what graph (nodes/edges/state) they run in,
how they hand off, where they can loop, and where a human must interrupt.

If Prompt 04/06 status is `provisional`, keep the graph to the minimum governed
workflow (fewest agents, no speculative parallelism) and mark this **provisional** too.

---

## Produce

**Artifact status (required):** `stable` | `provisional`

1. **Agent roster** — one row per agent: name, bounded context owned (from DDD), tools it may call (MCP names), authority limit, stop/escalation condition.
2. **LangGraph graph design** — nodes (= agents or deterministic steps), edges (conditional routing logic), the shared state schema, checkpointing strategy (what must survive a restart), and every HITL interrupt node.
3. **Planner/executor/critic pattern (if used)** — which agent plans, which executes tools, which verifies output before it reaches a human or downstream system; why this split (or why a simpler single-agent-per-workflow design was chosen instead — do not add multi-agent complexity without a stated reason).
4. **Memory design** — what persists across turns (short-term graph state vs long-term memory store), what must never persist (e.g. draft prohibited-decision text).
5. **Failure/loop-guard design** — max iterations per node, cycle-detection, what happens when an agent cannot make progress.
6. **Cross-workflow reuse** — which agents/subgraphs are shared across the three governed workflows (GxP batch review, PV intake, supply planning) vs workflow-specific.

### Lean / DMAIC lens (thin)

**Focus:** Improve (this design *is* the improvement over V1's single-shot app) + Control (loop guards, budgets).

1. Which named waste (from Prompt 01/04 registers) does splitting into multiple agents actually remove, vs risk adding (Integration/Context/Token waste from added hops)?
2. Loop-guard and token/tool-call budgets that make runaway agent loops a Control metric, not a hope.

---

## Exit criteria (handoff to Prompt 15)

- [ ] Every agent traces to a DDD bounded context and a named authority limit.
- [ ] Every HITL interrupt in the design matches a domain-critical decision from DDD §11.
- [ ] Loop guards and budgets are numeric, not aspirational.
- [ ] Artifact status stated; if `provisional`, graph is minimum governed workflow only.

---

## Constraints

- Do not add agents or parallelism without a stated waste/latency/quality reason.
- Do not let any agent design bypass a prohibited-decision boundary from DDD.
- Do not finalize MCP tool schemas here — that is Prompt 15.

---

## Output

Write under `docs/architecture/agentic/` **and mirror** to `workshop/participant-output/14-agentic-architecture/`:

- `agent_roster.md`
- `langgraph_design.md` (graph, state schema, checkpointing, HITL interrupts)
- `memory_design.md`
- `failure_and_loop_guards.md`
- `dmaic_lens.md` (thin)
