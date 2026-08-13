# knowledge

Domain knowledge base for the agentic system. **NAB-3 resolved (partially) at Stage 13:**
V2's `knowledge/` (32 pharma/GxP/PV/AI-governance policy documents) plus
`knowledge_catalog.csv` (the provenance/status/trust/supersession index) are copied here,
byte-verified against the catalog's own SHA-256 hashes.

**Why copy now, not before:** the ontology/semantic layer (Stage 13) is the first stage that
needs a *stable, version-controlled* source to build a knowledge-graph schema against — a
cross-repo reference into a gitignored sibling directory (983MB, not part of this repo) is not
reproducible for anyone who clones only this repo, and Stage 13's deliverables have to exist
independent of the V2 checkout being present on disk.

**Why this doesn't reopen ADR-002.** ADR-002 says V3 is built separately from V2 with **no
code reuse** — a decision about not inheriting V2's *application architecture*. This corpus is
domain **reference data**, not code: it is exactly the evidence Discovery, DDD, and this stage
already treat as the factual description of the domain (document statuses, authority model,
the two adversarial documents `FAKE_PV_EXPEDITED_RULE.md` / `MALICIOUS_SUPPLIER_DEVIATION.md`
used as poisoned-evidence test cases). Copying it is using V2 as the evidence source it was
always meant to be, not reusing V2's implementation.

**Scope boundary — NAB-3 only half-resolved.** This copy covers `knowledge/` only. V2's
`data/` (143 CSVs — eval/case fixtures like `batches.csv`, `icsr_cases.csv`) and `evaluation/`
(public fixtures, grader references) remain a **cross-repo reference**, left open for Stage 14
to decide, since fixture data is only needed once the eval harness exists to consume it.
Copying it now, unused, would be the Overproduction waste (O3) this programme already tracks.

See `docs/architecture/ontology/ontology.md` §1 for how this corpus grounds the ontology.
