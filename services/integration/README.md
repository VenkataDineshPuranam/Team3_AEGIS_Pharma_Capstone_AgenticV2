# integration

MCP servers and external tool/system integrations exposed to agents.

Stage 11 design docs: [tool_inventory.md](tool_inventory.md) (6 server registrations, 7 tool
contracts, one server per bounded context so retrieval scope is structural, not
caller-supplied), [prohibited_write_enforcement.md](prohibited_write_enforcement.md) (all
seven tools are read-only; the three-layer argument for why that's structural, not
incidental), [dmaic_lens.md](dmaic_lens.md). Contracts: `packages/contracts/tool_contracts/`.
No server code exists yet — Stage 20 is deliberately last.
