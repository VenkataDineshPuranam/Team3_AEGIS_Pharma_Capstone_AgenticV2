# Adaptation Notes — V2 Prompts → V3 Agentic Prompts

## Assessment

All 13 V2 prompts (`01_discovery.md` … `13_solution_proposal.md`) are **relevant and
reused with modification**. They were already written at the right altitude — evidence
discipline, DMAIC-Lean spine, DDD/C4/ADR sequencing, and (notably) `04_ddd.md` and
`06_c4.md` already had explicit RAG/agent/HITL sections, since V2's governed workflows
were AI-assisted even though the app itself was single-shot Q&A, not multi-agent.

## What changed

1. **Output paths (all 13 files)** — every "Write under `participant-outputs-v2/XX-name/`
   (and mirror to `specs/...`)" line was remapped to this repo's `.claude`-based structure
   (e.g. `docs/architecture/ddd/`, `docs/adr/`, `packages/contracts/`) with a mirror into
   `workshop/participant-output/` (this repo's equivalent of V2's `submission/artefacts/`).
   V2's `specs/` and `tasks/` top-level folders don't exist here; they map onto
   `packages/contracts/`, `tests/contract/`, and `plans/active/` respectively.

2. **`04_ddd.md` §10 (agent responsibilities)** — added a requirement to name each agent
   explicitly and flag bounded-context crossings at agent handoffs, since V3 is genuinely
   multi-agent (V2's language here was written generically enough to not need rewriting,
   just sharpening).

3. **`06_c4.md`** — added a required "Agentic runtime view" cross-cutting section: the
   LangGraph orchestration container, MCP tool-server containers, Redis cache container,
   and LangSmith/OTel observability container. V2's "Gen AI runtime sketch" bullet stayed
   as-is; this is additive.

4. **`08_technical_design.md`** — added §I2 "Agent/tool contracts": LangGraph state schema,
   per-agent node contracts, MCP tool contracts, cache contract, token/cost budget per node.
   V2 had no multi-agent runtime so had nothing to contract here.

5. **`12_assurance.md`** — added an "Agentic assurance" section: eval-ai-cache harness
   results, LangSmith trace review, threat-model verification, governance-hook firing
   check, compliance evidence check. V2's assurance prompt covered design fidelity/data
   authority/AI quality/operability/control generically; this adds the agent-specific
   verification V3 needs.

## What's new (no V2 equivalent)

Prompts `14`–`23` — see `PROMPT_LIBRARY.md` V3 addendum table. These cover exactly the
capabilities V2 never needed because it wasn't a multi-agent, tool-using, cached,
observed system: agentic architecture (LangGraph), MCP, skills/hooks, ontology/KG,
eval-ai-cache, performance tuning, governance/control, observability, AI security threat
modeling, and compliance (EU AI Act / ISO 42001).

## What did *not* need modification

`01_discovery.md`, `02_scqa_minto.md`, `03_prd_vision.md`, `05_feature_specs.md`,
`07_adrs.md`, `09_lean_dmaic.md`, `10_implementation_tasks.md`, `11_product_and_build.md`,
`13_solution_proposal.md` — reused as-is beyond the output-path remap. Their content
(evidence discipline, SCQA/Minto structure, feature/AC/BR modeling, ADR format, DMAIC
consolidation, task breakdown, build/proposal narrative) is domain- and
architecture-agnostic; it doesn't need to know whether the system underneath is
single-shot or multi-agent to do its job correctly. `11_product_and_build.md` gained one
note flagging that it now executes at Stage 20 (last), not immediately after Prompt 10.
