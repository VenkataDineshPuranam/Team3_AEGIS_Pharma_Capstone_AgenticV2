# Prompt 01 — Discovery (AI FDE Inputs)

**Lifecycle stage:** Discover  
**Framework derived:** Prerequisite evidence base (AI FDE inputs from the Lean–DMAIC mental model)  
**Core question:** What exists, how does it connect, and what can we trust?  
**Prerequisites:** Access to the repository, codebase, and/or source materials (may be scarce).  
**Does not derive yet:** SCQA narrative, DDD model, C4, ADR, full Lean plan, or target architecture.

---

## Intent

Establish the factual foundation for every later framework. Collect **business context, user workflow, constraints, evidence, and stakeholder needs** without proposing a solution architecture.

When materials are thin, Discovery still runs — but it must **score sufficiency**, produce an **evidence acquisition backlog**, and declare whether Prompt 02 may be **decision-ready** or **hypothesis-only**.

Lean/DMAIC runs here as a **full Define → Measure → Analyze → Improve → Control cycle** plus full DOWNTIME and AI-specific waste registers — Discovery is one of the designated full-DMAIC stages (with Frame/02, DDD/04, C4/06, ADR/07). Improve/Control content at this stage is necessarily provisional (no architecture exists yet) and must be labeled as such, not withheld.

---

## Entry criteria

- Whatever source materials exist are available for inspection (complete pack not required).
- Engagement scope (systems / repos in bounds) is stated.
- Known access gaps (no prod data, no SME, no SoT docs) are listed up front if known.

---

## Produce

1. **Repository and source-system map** — what exists, where it lives, and how it connects.
2. **Entities, identifiers, and timestamp semantics** — what is tracked, how it is named, and what time means in each context (event time vs report time if observable).
3. **Evidence ownership and authority** — source of truth for each material data class; who or what may assert it.
4. **Material inconsistencies, gaps, and conflicts** — where data disagrees, is missing, or cannot be trusted.
5. **Stakeholder decisions and decision horizons** — decided, pending, and timeframes.
6. **Constraints register** — technical, risk, compliance, security, privacy, and operational constraints already visible in evidence.
7. **Current-state workflow sketch** — how work is done today (as observed, not redesigned). Mark inferred steps as assumptions.
8. **Fact / derivation / assumption / question register** — classify every material finding into exactly one category.
9. **Top ten investigation hypotheses** — ranked by impact on later framing and design.

10. **AI FDE input sufficiency score** — rate each input **Strong / Partial / Missing**:

    | AI FDE input | Score | What exists | What is missing |
    |--------------|-------|-------------|-----------------|
    | Business context | | | |
    | User workflow | | | |
    | Constraints | | | |
    | Evidence (data, logs, research) | | | |
    | Stakeholder needs | | | |

    **Overall framing mode (required):**
    - `decision-ready` — Situation/Complication can be written mainly from facts/derivations; no critical inventing.
    - `hypothesis` — one or more inputs are Partial/Missing such that framing must proceed as a testable hypothesis, not a locked decision.

    Rule of thumb: if **Evidence** or **User workflow** is Missing, or two+ inputs are Missing, default to `hypothesis` unless a reviewer explicitly overrides.

11. **Evidence acquisition backlog** — ordered list of what to obtain next. For each item: artifact needed, likely owner/source, why it blocks (which later prompt), and priority (blocks framing / blocks design / blocks production).

12. **Full DOWNTIME and AI-specific waste registers** — while inspecting the current workflow, register every observed or hypothesized waste against all 8 DOWNTIME categories and all 8 AI-specific categories (see Lean/DMAIC lens below for the full format). Mark each as **observed** vs **hypothesized**. Do not redesign the process here — that is Improve, captured provisionally in the lens below.

### Lean / DMAIC lens (spine — FULL at this stage)

**DMAIC focus this stage:** run the **full** Define → Measure → Analyze → Improve → Control cycle now, not a thin Measure-only signal. Discovery is a designated full-DMAIC stage (alongside Frame/02, DDD/04, C4/06, ADR/07); PRD/05/Technical Design/08/09–13 remain thin/consolidation stages as before.

In `dmaic_lens.md`, record the full cycle:

1. **Define** — the improvement problem and scope, drawn from the business context gathered in this stage (not yet an architecture decision).
2. **Measure** — what can already be measured (cycle time, error rate, backlog, token/cost signals, review lag); list every baseline that is **Unknown**, explicitly, rather than estimating it.
3. **Analyze** — root causes visible from Discovery evidence alone (Pareto / fishbone / 5 Whys where evidence supports it); label conclusions that rest on assumption rather than measured data.
4. **Improve** — candidate treatment classes worth carrying into Frame/PRD/DDD (standardisation, deterministic validation, master-data resolution, risk-tiered review, constrained/grounded AI, non-AI fixes first) — mark these **provisional**, since no architecture exists yet to validate them against.
5. **Control** — what governance/ownership/revisit-trigger questions this stage already surfaces, to be firmed up once Prompt 09 consolidates and Prompt 12 closes Control.

Also produce, in full (not abbreviated):

- **DOWNTIME waste register** — all 8 categories (Defects, Overproduction, Waiting, Non-utilised talent, Transportation, Inventory, Motion, Extra processing), each with observed vs hypothesized, magnitude, impact, VA/business-required-NVA/pure-waste classification, and eliminate/simplify action.
- **AI-specific waste register** — all 8 categories (Token, Retrieval, Model, Human-review, Evaluation, Integration, Context, Observability), each with where/how it appears, evidence trace, magnitude, impact, recommended treatment.

This full analysis becomes a direct input to Prompt 02 (Frame/SCQA), not just a signal list — Frame's Situation/Complication should cite this stage's Define/Measure/Analyze findings directly.

---

## Exit criteria (handoff to Prompt 02)

- [ ] Sources of truth and trust gaps are explicit.
- [ ] No target architecture, tool selection, or full risk model is proposed.
- [ ] Assumptions and open questions are separated from facts.
- [ ] Sufficiency scores and **framing mode** (`decision-ready` or `hypothesis`) are declared.
- [ ] Evidence acquisition backlog exists whenever any input is Partial or Missing.
- [ ] Full DOWNTIME and AI-specific waste registers and a full `dmaic_lens.md` (Define/Measure/Analyze/Improve/Control) exist (even if entries are "none observed" or "provisional — revisit at Prompt 09").
- [ ] If `decision-ready`: enough evidence exists to write Situation and Complication without inventing facts.
- [ ] If `hypothesis`: Situation/Complication may use labeled assumptions; inventing unlabeled “facts” is still forbidden.

---

## Constraints

- Do not propose a target architecture or solution design.
- Do not invent domain language; quote or flag ambiguous terms for Prompt 04 (DDD).
- Prefer evidence citations (path, system, artifact) over unsupported claims.
- Do not upgrade `hypothesis` to `decision-ready` without new evidence.
- Do not present waste-register entries or Improve/Control content as measured baselines or locked decisions — label them observed/hypothesized and provisional respectively.
- Full DMAIC and full waste registers ARE required at this stage (Discovery is a designated full-DMAIC stage); what remains deferred to Prompt 09 is cross-stage *consolidation*, not the first full pass.

---

## Output

Write under `docs/product/discovery/` **and mirror** to `workshop/participant-output/01-discovery/`:

- `evidence_register.md` (includes sufficiency scores and framing mode)
- `evidence_acquisition_backlog.md` (required if any input is Partial or Missing; otherwise note “none”)
- `dmaic_lens.md` (full Define/Measure/Analyze/Improve/Control)
- `waste_register_downtime.md` (full 8-category DOWNTIME register)
- `waste_register_ai_specific.md` (full 8-category AI-specific register)
