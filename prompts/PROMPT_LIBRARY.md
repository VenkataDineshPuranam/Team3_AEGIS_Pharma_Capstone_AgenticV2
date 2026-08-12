# Participant Prompt Library

These prompts guide engineering work and do not contain solution content. Always require evidence paths, distinguish facts from assumptions, and write outputs under `submission/`.

## 1. Qualify the problem

“Using only supplied evidence, define the measurable workflow problem, affected decisions, baseline, no-AI alternative, constraints, uncertainty and stop criteria. Cite every factual claim.”

## 2. Map evidence authority

“For [object/workflow] and [as-of time], map identity, source, authority, status, effective date, jurisdiction, unit, terminology, lineage, conflicts and missing evidence. Do not resolve a conflict without a documented rule.”

## 3. Derive requirements and tests

“Convert the selected workflow and injects into uniquely identified functional, non-functional, GxP, safety, security, privacy, reliability and economics requirements. For each, produce measurable acceptance criteria and at least one failing and passing test.”

## 4. Threat-model a design

“Analyse prompt injection, poisoning, tool abuse, stale authorization, replay, exfiltration, excessive agency, supply-chain compromise and denial-of-wallet. Map each threat to controls, negative tests, logs, response and residual risk.”

## 5. Review a candidate output

“Check the output against the relevant JSON contract and evidence. Flag fabrication, missing provenance, authority/effective-date errors, silent conversion, overclaiming, prohibited decisions, unhandled uncertainty and missing human review.”

## 6. Prepare the defence

“Build an inspection-ready claim–argument–evidence narrative. Include the strongest counterevidence, failed gates, residual risks, vendor/continuity limits, and the precise decision requested.”

---

## V3 addendum — agentic AI prompts

Prompts `01`–`13` are carried forward from V2 (see `ADAPTATION_NOTES.md` for what changed:
output paths remapped to this repo's `.claude`-based structure, plus targeted additions in
`04_ddd.md` §10, `06_c4.md` (agentic runtime view), `08_technical_design.md` §I2, and
`12_assurance.md` (agentic assurance) for multi-agent/LangGraph/MCP/cache concerns).

Prompts `14`–`23` are new — V2 had no multi-agent runtime, so it needed no orchestration,
tool-contract, skills/hooks, ontology, eval-cache, performance, governance, observability,
security, or compliance stage of its own:

| Prompt | Stage (STAGES.md) | Topic |
|---|---|---|
| 14 | 10 | Agentic architecture (LangGraph multi-agent design) |
| 15 | 11 | MCP servers & tool contracts |
| 16 | 12 | Skills & hooks |
| 17 | 13 | Ontology, knowledge graph, semantic layer |
| 18 | 14 | Eval-AI-Cache (eval harness + response cache) |
| 19 | 15 | Performance tuning (Redis, cache, token economics) |
| 20 | 16 | Governance & control |
| 21 | 17 | Observability (LangSmith, OpenTelemetry) |
| 22 | 18 | AI security threat modeling |
| 23 | 19 | Compliance (EU AI Act, ISO 42001) |

Stage 20 (repo implementation / app build) and Stage 21 (documentation) close the loop using
Prompt 11 (build) and Prompt 13 (solution proposal) patterns, executed **last**, after all of
the above are stable.
