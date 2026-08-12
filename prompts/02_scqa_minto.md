# Prompt 02 — SCQA & Minto Pyramid (Frame)

**Lifecycle stage:** Frame  
**Framework derived:** SCQA + Minto Pyramid Principle (including MECE)  
**Core question:** Why does this matter, and what is the ask?  
**Prerequisites:** Prompt 01 evidence register (with framing mode and sufficiency scores).  
**Primary output type:** Decision narrative or hypothesis narrative (pyramid-structured).

---

## Intent

Derive the **framing framework**: turn discovery evidence into a clear, audience-ready narrative. Lead with the answer (Minto), structure the story as **Situation → Complication → Question → Answer** (SCQA), and support the answer with **MECE** key points and evidence.

Respect Prompt 01 **framing mode**:

| Mode | Meaning |
|------|---------|
| `decision-ready` | Narrative supports a capability decision; pyramid rests mainly on facts/derivations. |
| `hypothesis` | Narrative frames a **testable recommendation**; Answer is an experiment / learning plan, not a locked build mandate. |

---

## Entry criteria

- Prompt 01 exit criteria are met.
- Framing mode is declared (`decision-ready` or `hypothesis`).
- Facts vs assumptions are labeled; critical open questions are listed.
- Evidence acquisition backlog is available if mode is `hypothesis`.

---

## Produce

### 0. Narrative class (required)

State at the top of the output:

- **Narrative class:** `decision-ready` | `hypothesis` (must match Prompt 01 unless new evidence upgraded it — document the upgrade).
- **Evidence boundary:** what this narrative is allowed to claim.
- **Top blocking acquisition items** (from Prompt 01 backlog) that keep the class at `hypothesis`, if applicable.

### A. SCQA narrative

1. **Situation** — current state of operations, relevant facts, concise context. Prefer facts/derivations; label assumptions.
2. **Complication** — compound problem across applicable dimensions (operational, technical, financial, regulatory, human, environmental, security, data, or domain-specific).
3. **Question** — one bounded decision or engineering question that must be answered.
4. **Answer**
   - `decision-ready`: capability-level recommendation **without** preselecting architecture, vendor, or model.
   - `hypothesis`: capability-level **recommended experiment** — what to test, what would falsify it, and what evidence must be acquired before locking a decision.

Also define:

- desired outcomes and what “good” looks like;
- audience, decision horizon, evidence boundary, and authority boundary;
- measurable outcomes (baselines marked known vs unknown);
- explicit exclusions (what this decision does **not** cover).

### B. Minto Pyramid view of the Answer

Present the Answer as a pyramid:

1. **Governing answer** — one clear recommendation (or governing experiment in hypothesis mode).
2. **MECE key supporting points** (typically 3–7) — mutually exclusive, collectively exhaustive.
3. **Support under each point** — cite Prompt 01 facts/derivations; in `hypothesis` mode, assumptions are allowed **only if labeled** and tied to acquisition backlog items.

### C. Framing handoff pack

- Decision question locked for PRD / DDD (or provisional question if `hypothesis`).
- Success metrics that later PRD and DMAIC Measure/Control can use (note missing baselines).
- Open questions that block design (must be resolved or explicitly assumed).
- Whether later artifacts (PRD through ADR) must be marked **provisional**.

### Lean / DMAIC lens (spine — FULL at this stage)

**DMAIC focus this stage:** run the **full** Define → Measure → Analyze → Improve → Control cycle, building directly on Prompt 01's full DMAIC output and waste registers — do not restart from a blank page. Frame is a designated full-DMAIC stage (with Discovery/01, DDD/04, C4/06, ADR/07).

In `dmaic_lens.md`, record the full cycle:

1. **Define** — the improvement problem restated at Frame level: what waste or rework does the Complication describe (map to DOWNTIME / AI waste names using Prompt 01's registers)?
2. **Measure** — which success metrics from the Answer are Measure targets (known vs Unknown baseline, carried from Prompt 01, refined here)?
3. **Analyze** — do Prompt 01's root-cause findings still hold at Frame level, or does the SCQA narrative surface a root cause Prompt 01 missed? Note any correction.
4. **Improve** — how the Answer (governing recommendation or governing experiment) is itself the Improve candidate — state explicitly how it reduces waste without adding model/process waste, and what alternative Improve options were rejected and why.
5. **Control** — what would have to be monitored post-decision for this Answer to be judged as working (provisional; firmed up in Prompt 09/12).

Carry forward and refine, rather than re-deriving from scratch:

- **DOWNTIME waste register** (`waste_register_downtime.md`) — update Prompt 01's register with any Frame-stage findings.
- **AI-specific waste register** (`waste_register_ai_specific.md`) — same.

---

## Exit criteria (handoff to Prompt 03)

- [ ] Narrative class is stated and consistent with Prompt 01 (or documented upgrade).
- [ ] SCQA is complete; claims do not invent unlabeled facts.
- [ ] Pyramid is MECE; each support item is fact, derivation, or labeled assumption.
- [ ] In `decision-ready` mode: Answer is capability-level and evidence-backed.
- [ ] In `hypothesis` mode: Answer is an experiment with falsifiers and acquisition needs.
- [ ] Answer stays at capability level (no C4/tool lock-in).
- [ ] One bounded question is ready to drive PRD and domain modeling.
- [ ] Full `dmaic_lens.md` (Define/Measure/Analyze/Improve/Control) and updated waste registers are complete (feeds Prompt 09 consolidation).

---

## Constraints

- Do not write the full PRD, feature flows, bounded contexts, containers, or ADRs here.
- Do not expand scope beyond the evidence boundary without labeling new items as assumptions.
- Do not present a `hypothesis` narrative as if it were `decision-ready`.
- Full DMAIC and full waste registers ARE required at this stage; what remains deferred to Prompt 09 is cross-stage *consolidation* across all designated full-DMAIC stages, not the first full pass.
- Think top-down; communicate so the audience sees answer → reasons → evidence/assumptions.

---

## Output

Write under `docs/product/scqa/` **and mirror** to `workshop/participant-output/02-scqa/`:

- `scqa.md`
- `dmaic_lens.md` (full Define/Measure/Analyze/Improve/Control)
- `waste_register_downtime.md` (updated from Prompt 01)
- `waste_register_ai_specific.md` (updated from Prompt 01)
