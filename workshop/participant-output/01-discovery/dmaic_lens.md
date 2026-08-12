# DMAIC Lens — Stage 01 (Discovery)

**Full cycle** (Discovery is a designated full-DMAIC stage per `prompts/01_discovery.md`).

## Define

The improvement problem: V2 delivers governed pharma decision-support as a **single-shot,
document-driven** exercise — one prompt-in, one contract-out, evaluated by a deterministic
grader harness. This is safe and well-governed, but does not exercise (and cannot teach)
the operational realities of a **multi-agent, tool-using, cached, continuously observed**
AI system, which is now the explicit target (user's decision, `evidence_register.md` §5).
The problem this stage resolves: establish, from evidence, what carries forward from V2
unchanged (domain, constraints, eval floor) versus what must be newly designed (agent
topology, tool contracts, cache, governance, observability) — without inventing facts
about a target architecture that does not exist yet.

## Measure

Baselines available from V2, directly countable this pass:
- 143 CSV datasets (`data/`), 32 knowledge documents (`knowledge/`) — Fact.
- 15 public eval fixtures, 4 JSON response contracts, 12 required eval categories
  (`evaluation/EVALUATION_PLAN.md`, `evaluation/public_fixtures/`) — Fact (files confirmed;
  category count from `evaluation/EVALUATION_PLAN.md`, not re-read line-by-line this pass —
  treat count as **derivation** carried from prior exploration).
- Baselines that are **Unknown** (must not be estimated): V3 token cost per workflow run,
  V3 agent count, V3 latency per workflow, V2's actual eval scorecard results (never read
  the numbers in `submission/evaluation/reports/scorecard.csv` this pass), V2's rubric
  point totals achieved by the prior completed run.

## Analyze

Root causes visible from Discovery evidence alone:
- V2's single-shot architecture is a root cause of the exact gap the user is asking V3 to
  close (no multi-agent orchestration, governance-as-code, or observability existed to
  need architecting). This is a **derivation** (inferred from the absence of
  orchestration/governance code in `submission/app-advanced`'s route list), not a directly
  measured fact.
- The tension between V2's "offline-compatible" framing and a LangSmith-based observability
  stack (hosted service) is a genuine root-cause risk for Stage 04's target architecture,
  not yet resolved — labeled explicitly as **assumption pending resolution** (EAB-2).

## Improve (provisional — no architecture exists yet)

Candidate treatment classes to carry into Stage 02 (SCQA) and beyond, marked
**provisional**:
- Preserve V2's domain model, constraints, and eval floor unchanged; treat the agentic
  redesign as additive, not a domain rewrite (reduces risk of re-litigating already-settled
  GxP/PV/supply domain rules).
- Resolve the offline/hosted tension explicitly as an ADR (Stage 08) rather than letting it
  remain an implicit assumption through the whole design.
- Quantify token/cost budgets (EAB-6) before committing to agent topology, to avoid
  building an over-engineered multi-agent system and later paying Stage 15 rework cost.

## Control

Governance/ownership/revisit-trigger questions surfaced here, to be firmed up at Stage 09
(consolidation) and Stage 12 (assurance):
- Who owns the decision on EAB-1 (rubric applicability) and EAB-4 (audience)? — currently
  unowned; needs a named owner before Stage 21.
- Revisit trigger: if EAB-2 (offline/hosted tension) resolves toward "hosted-only," several
  V2 non-negotiables framed around offline-compatibility should be explicitly revised, not
  silently dropped.
