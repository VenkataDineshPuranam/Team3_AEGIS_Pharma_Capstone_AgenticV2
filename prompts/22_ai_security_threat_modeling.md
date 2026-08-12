# Prompt 22 — AI Security Threat Modeling

**Maps to:** STAGES.md Stage 18 (`stage-18-ai-security`)
**Lifecycle stage:** Design + Verify (security)
**Framework derived:** V3 addition, extending PROMPT_LIBRARY.md item 4 (threat-model a design) into a full stage; STRIDE-for-AI style.
**Core question:** How could this multi-agent system be attacked or misused, and what stops it?
**Prerequisites:** Prompt 14 (agent/graph design), Prompt 15 (tool contracts), Prompt 17 (knowledge graph/retrieval).

---

## Produce

1. **Threat catalogue** — for this multi-agent system specifically: prompt injection (direct + indirect via retrieved documents), tool abuse / excessive agency, cache poisoning (Prompt 18/19's cache), agent-to-agent trust exploitation, memory/context poisoning, stale-authorization replay, data exfiltration via tool output, supply-chain compromise (MCP servers, model providers), denial-of-wallet.
2. **Abuse-case scenarios** — concrete attack narratives per threat, mapped to which agent/node/tool is the entry point.
3. **Controls mapping** — each threat → control (hook, policy, contract validation) → negative test (`tests/security/`) → residual risk rating.
4. **Red-team notes** — what was actually attempted against the built system (once Stage 20 exists) vs theoretical only.

### Lean / DMAIC lens (full — security is a designated full-DMAIC stage alongside Discovery/Frame/DDD/C4/ADR)

1. **Define** — which attack surface is new because this is multi-agent/tool-using (vs V2's single-shot app)?
2. **Measure** — which threats have a negative test today vs none?
3. **Analyze** — root cause per threat (missing input validation, over-broad tool authority, unbounded retrieval).
4. **Improve** — the control that closes each gap.
5. **Control** — which control needs a runtime monitor (feeds Prompt 21 observability), not just a design doc.

---

## Exit criteria (handoff to Prompt 23)

- [ ] Every threat category has a control and a negative test.
- [ ] Every write-capable MCP tool (Prompt 15) has a documented abuse case and control.
- [ ] Residual risk register exists for anything not fully mitigated.

---

## Output

Write under `security/threat-models/`, `security/abuse-cases/`, `tests/security/` **and mirror** to `workshop/participant-output/22-ai-security/`:

- `threat_catalogue.md`
- `abuse_cases/*.md`
- `controls_mapping.md`
- `residual_risk_register.md`
- `dmaic_lens.md` (full)
