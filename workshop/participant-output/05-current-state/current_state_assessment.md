# Current State of the Repo — Stage 05

**Executes:** `prompts/01_discovery.md`, applied reflexively to this V3 repository itself.
**DMAIC focus:** Measure.
**Measured as of:** 2026-08-12, branch `stage-05-current-state`, forked from
`stage-04-adr` at commit `0961cc5`.

**Re-measured note:** an earlier version of this document was produced when this stage ran
as Stage 02, before DDD/C4/ADR existed. A sequencing correction moved it to run *after* ADR
(`SPEC_DRIVEN_DEVELOPMENT.md` §3), which made the original measurement stale — it counted
184 files when only Stage 01 had real content. The numbers below are re-measured against
the repo as it actually stands now, which is the whole point of a "current state" document.

---

## 1. Repository map (measured)

| Top-level folder | Tracked files | Real content vs. stub |
|---|---|---|
| `docs/` | 59 | **Substantially real** — `docs/adr/` (14), `docs/architecture/` (20: ddd + c4), `docs/product/` (16: discovery, scqa, state) all hold Stage 01–04 output. `docs/engineering/`, `docs/operations/`, `docs/security/` remain README-only stubs (1 each), owned by later stages |
| `workshop/` | 47 | **Real mirrors** of Stages 01–04 output (`01-discovery`, `02-scqa`, `04-ddd`, `05-current-state`, `06-c4`, `07-adr`) + README-only stubs for `scenarios/`, `labs/`, `checkpoints/`, `assessments/` |
| `eval-ai-cache/` | 29 | **Real, unconsumed** — user-seeded brownfield-evals/Redis/OTel runbook library. Stage 14 is its first consumer; still untouched |
| `prompts/` | 25 | **Real** — 13 adapted V2 prompts + 10 new V3 prompts (14–23) + library/adaptation notes |
| `templates/` | 10 | **Stub** — blank artefact templates, none filled |
| `evidence/` | 10 | **Stub** — all 9 subfolders README-only. Correct for now: nothing has shipped, so there is no execution evidence to record. Becomes load-bearing at Stage 19 (compliance) |
| `.claude/` | 9 | **Partial** — `mcp.json`/`hooks.json`/`settings.json` are empty scaffolds; `skills.md`/`hooks.md` are zero-row indexes. Stage 11/12 own populating them |
| `tests/` | 8 | **Stub** — zero actual tests. Correct: no implementation exists to test (Stage 20 is last) |
| `security/`, `ops/`, `infra/` | 6 each | **Stub** — owned by Stages 15–18 |
| `packages/` | 5 | **Stub** — owned by Stage 20 |
| `quality/`, `deploy/` | 4 each | **Stub** |
| `services/`, `plans/` | 3 each | **Stub** |
| `apps/` | 2 | **Stub** — Stage 20 |
| `knowledge/`, `evaluation/`, `runbooks/` | 1 each | **Seeded this stage's earlier run** (was 0 — see §4) |

**Total tracked files: 249** (up from 184 at the original Stage 02 measurement; the delta is
Stages 02–04's DDD/C4/ADR output plus its `workshop/` mirrors).

## 2. Branch/commit state

| Item | Value |
|---|---|
| `main` | at `57d0b92` — deliberately **not** kept in sync, per standing user instruction (work syncs across stage branches, not to `main`) |
| Stage branches | 21 branches, `stage-01`…`stage-21`, renamed once during the resequencing |
| Stages complete | 01 (discovery/SCQA), 02 (DDD), 03 (C4), 04 (ADR) — 4 of 21 |
| Artifact statuses | DDD and C4 are `provisional`; 4 ADRs `accepted`, 4 `proposed`; architecture review `conditional` |

## 3. Material gaps and open items (measured now, not assumed)

1. **Two blockers carried from the architecture review** (`docs/adr/architecture_review.md`):
   - **EAB-2** — air-gap requirement unconfirmed. Escalated in this session's summary to the
     user; still unanswered. Can reopen ADR-001 (the entire runtime stack).
   - **EAB-3** — no real HITL/context owner names. This is what keeps DDD `provisional`, and
     transitively keeps C4 `provisional` and 4 ADRs `proposed`.
2. **`plans/active/` remains empty** (NAB-2 from the original run, still open). The
   `SPEC_DRIVEN_DEVELOPMENT.md` method says stage specs go there first, but every stage so
   far has been driven directly by its `prompts/` file. Either the method doc should be
   corrected to say prompt-driven stages need no separate plan file, or the practice should
   change. **Unresolved — recommend correcting the method doc**, since duplicating a spec
   that already exists in `prompts/` is exactly the "nothing was written twice" violation the
   SDD reference warns against.
3. **`knowledge/`, `evaluation/`, `runbooks/` hold README stubs only** (NAB-3, open). Whether
   V2's 32 knowledge docs and evaluation fixtures should be copied locally or kept as
   cross-repo references is still a scope decision. ADR-002 (build separately) leans toward
   local copies for self-containment, but does not settle it.
4. **`eval-ai-cache/`'s 29-file runbook library remains entirely unconsumed** — 24 numbered
   brownfield-eval playbook files plus Redis and OpenTelemetry runbooks. This is the single
   largest body of directly-applicable material sitting unused; Stages 14/15/17 should draw
   on it rather than deriving equivalents from scratch.

## 4. Closed since the original measurement

- **NAB-1 (closed).** `knowledge/`, `evaluation/`, `runbooks/` had zero tracked files despite
  `README.md` claiming they were carried forward from V2 — a documented-vs-actual
  contradiction. Seeded with README stubs stating their purpose and current
  reference-not-copy status.
- **The "verify V2 grader behavior" action item (closed).** Raised at Stage 03, executed at
  Stage 04, and it found a real error — see ADR-003.

## 5. Fact / derivation / assumption / question register

| # | Item | Class |
|---|---|---|
| 1 | 249 tracked files; 4 of 21 stages complete | **Fact** (measured this pass) |
| 2 | DDD/C4 `provisional`; 4 ADRs `proposed`; review `conditional` | **Fact** |
| 3 | `eval-ai-cache/` is unconsumed | **Fact** |
| 4 | Correcting the method doc is the right resolution for the `plans/active/` gap rather than retro-filling plan files | **Derivation** — follows from the SDD reference's "nothing was written twice" principle |
| 5 | Whether V2's knowledge/eval content should be copied locally | **Question** — open (NAB-3) |

## 6. Next-actions backlog

| ID | Item | Blocks | Priority |
|---|---|---|---|
| NAB-2 | Resolve the `plans/active/` method-vs-practice mismatch (recommend: correct the method doc) | Nothing hard; a documentation-accuracy issue | Low-medium |
| NAB-3 | Decide whether to copy V2's `knowledge/`/`evaluation/` content locally | Stage 13 (ontology needs domain knowledge), Stage 14 (eval floor) | Medium |
| NAB-4 (new) | Draw on `eval-ai-cache/`'s runbook library when Stages 14/15/17 begin, rather than re-deriving | Stages 14, 15, 17 | Medium |
| EAB-2 | **Air-gap requirement** — sponsor/user confirmation | Stage 20; can reopen ADR-001 | **High** |
| EAB-3 | **Real HITL/context owners** | Stage 16; unblocks DDD → `stable` | **High** |

---

## Lean / DMAIC lens

See `dmaic_lens.md` (this folder).
