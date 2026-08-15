# Prompt 15 — MCP Servers & Tool Contracts

**Maps to:** STAGES.md Stage 11 (`stage-11-mcp`)
**Lifecycle stage:** Design (integration)
**Framework derived:** V2 addition — Model Context Protocol tool contracts.
**Core question:** What tools may agents call, with what authority, and what do they return?
**Prerequisites:** Prompt 14 agentic architecture (agent roster + tool names referenced).

---

## Produce

1. **Tool inventory** — one entry per MCP tool: name, owning service (`services/integration/`), read-only vs write, which agent(s) may call it.
2. **Tool contract per tool** — input/output JSON schema, error cases, idempotency guarantee, authorization requirement, rate limit.
3. **Prohibited-write enforcement** — for every tool that could touch a governed system (batch records, PV case data, allocation systems), state explicitly how the tool refuses/cannot execute a terminal decision (this must match the DDD prohibited-action boundary, not just be a prompt instruction).
4. **`.claude/mcp.json` registration** — the actual server registration entries.

### Lean / DMAIC lens (thin)

1. Which tool contracts prevent Integration waste (agents guessing at undocumented APIs)?
2. Which tool calls are cacheable (feeds Prompt 18 eval-ai-cache) vs must never be cached (state-mutating, or feeding a prohibited decision)?

---

## Exit criteria

- [ ] Every tool an agent can call (per Prompt 14 roster) has a contract here.
- [ ] Every write-capable tool has an explicit prohibited-action refusal mechanism, not just documentation.
- [ ] `.claude/mcp.json` reflects the tool inventory.

---

## Output

Write under `services/integration/` and `packages/contracts/` **and mirror docs** to `workshop/participant-output/15-mcp/`:

- `tool_inventory.md`
- `tool_contracts/*.schema.json`
- `prohibited_write_enforcement.md`
- `dmaic_lens.md` (thin)
