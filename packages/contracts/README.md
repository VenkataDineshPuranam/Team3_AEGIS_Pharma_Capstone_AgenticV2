# contracts

Shared API/tool/MCP contracts and JSON schemas used across services and agents.

`tool_contracts/` — 9 MCP tool contracts (`docs.../services/integration/tool_inventory.md`
is the design doc; these are the JSON Schema definitions it produces). All read-only; each
carries `contract_version`, an idempotency key, and a `what_this_schema_cannot_express` block
for the contracts closest to a governed decision.
