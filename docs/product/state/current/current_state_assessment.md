# Current State of the Repo — Stage 02

**Executes:** `prompts/01_discovery.md`, applied reflexively to this V3 repository itself
(per `SPEC_DRIVEN_DEVELOPMENT.md`'s stage table: Stage 02's driving prompt).
**DMAIC focus:** Measure (this stage is not a designated full-DMAIC stage; see `dmaic_lens.md`).
**Measured as of:** 2026-08-12, branch `stage-02-current-state`, forked from
`stage-01-discovery-scqa` at commit `2bf4e53`.

---

## 1. Repository map (measured, not estimated)

Direct counts via `git ls-files`, this session:

| Top-level folder | Tracked files | Real content vs. stub |
|---|---|---|
| `docs/` | 30 | **Mixed** — `docs/product/discovery/`, `docs/product/scqa/` have real Stage 01 content (10 files); `docs/adr/`, `docs/engineering/`, `docs/operations/`, `docs/security/` are still README-only stubs (1 file each) |
| `eval-ai-cache/` | 29 | **Real** — user-seeded brownfield evals/Redis/OTel runbook library (24-file runbook + 2 docx + 1 zip + 1 png), not yet consumed by any stage |
| `prompts/` | 25 | **Real** — 13 ported+adapted V2 prompts, 10 new V3 prompts (14–23), `PROMPT_LIBRARY.md`, `ADAPTATION_NOTES.md` |
| `workshop/` | 14 | **Mixed** — `participant-output/01-discovery/`, `02-scqa/` have real mirrored content (8 files); `scenarios/`, `labs/`, `checkpoints/`, `assessments/` are README-only stubs |
| `templates/` | 10 | **Stub** — 10 blank artefact templates (`adr.md`, `threat-model.md`, etc.), none filled in yet |
| `evidence/` | 10 | **Stub** — all 9 subfolders are README-only; no actual evidence recorded (expected — nothing has shipped yet) |
| `.claude/` | 9 | **Partial** — `mcp.json`, `hooks.json`, `settings.json` exist as empty scaffolds; `skills/skills.md`, `hooks/hooks.md` are indexes with zero rows; `agents/`, `rules/` are README-only stubs |
| `tests/` | 8 | **Stub** — all 8 subfolders README-only, zero actual tests |
| `security/`, `ops/`, `infra/` | 6 each | **Stub** — README-only |
| `packages/` | 5 | **Stub** — README-only |
| `quality/`, `deploy/` | 4 each | **Stub** — README-only |
| `services/`, `plans/` | 3 each | **Stub** — README-only (`plans/active|completed|superseded/` all empty of actual specs — see gap below) |
| `apps/` | 2 | **Stub** — README-only |
| `knowledge/`, `evaluation/`, `runbooks/` | **0 → 1 each** | **Gap, closed this stage** — these three folders had zero tracked files, not even a README (see §4); seeded with README stubs as part of this stage's own next-actions (NAB-1) rather than left open |
| Root files | 10 | **Real** — `README.md`, `SPEC_DRIVEN_DEVELOPMENT.md`, `STAGES.md`, `STRUCTURE_MANIFEST.json`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `REPO_MAP.md`, `LICENSE`, `.gitignore` |

**Total tracked files: 184 at measurement time, 187 after closing NAB-1 within this stage
(README stubs added to `knowledge/`, `evaluation/`, `runbooks/`).**

## 2. Branch/commit state

| Item | Value |
|---|---|
| `main` | at `57d0b92` ("Stage 01: execute Discovery + SCQA/Minto…") — **one commit behind** the stage branches by explicit user instruction (do not auto-sync renames to `main`) |
| All 21 `stage-NN-*` branches | fast-forwarded to `2bf4e53` ("Rename Stage 01/02 primary documents…") as of the rename work |
| Stage 01 | **stable** per `STAGES.md` — only stage with real design-artefact content |
| Stages 02–21 | **not started** per `STAGES.md`, though scaffolding (folders + README stubs) exists for all of them from Stage 00 |

## 3. Entities (repo-reflexive reading of Prompt 01 §2)

Applying "entities, identifiers, timestamp semantics" to the repo itself:

- **Stage** — identified by two-digit number + slug (`00-foundation` … `21-documentation`), tracked in `STAGES.md`. Status values: `not started` → `spec drafted` → `in review` → `stable`.
- **Branch** — one per stage, named `stage-NN-slug`, currently all pointer-equal (no stage has diverged content from another except 01).
- **Prompt** — numbered `01`–`23` in `prompts/`, each declares its own entry/exit criteria (its own internal "identifier scheme" independent of the stage numbering — see the Driving-prompt column in `SPEC_DRIVEN_DEVELOPMENT.md` §3 for the mapping, since prompt numbers and stage numbers diverge from Stage 10 onward: e.g. Stage 10 is driven by Prompt 14).
- **Artefact** — a file under `docs/`, `evidence/`, etc.; "real" vs "stub" is the only status distinction measured this pass (no finer artefact-status metadata exists yet).

## 4. Material inconsistencies, gaps, and conflicts (measured this pass)

1. **`knowledge/`, `evaluation/`, `runbooks/` were empty — not even a README.** These three
   folders were created in the very first (pre-canonical-structure) scaffold pass and never
   re-seeded when the repo pivoted to the `.claude`-based 15-section pattern
   (`README.md`'s "carried forward / extended from V2" list names them, but nothing was
   actually carried forward into them). This was a **direct contradiction between
   `README.md`'s stated structure and the actual filesystem** — a defect, not a design
   choice. **Closed within this stage** (NAB-1, §7) with README stubs stating what each
   folder is for and that it currently references V2's sibling directory rather than
   holding a local copy — the local-copy decision itself remains NAB-3, still open.
2. **`plans/active/`, `plans/completed/`, `plans/superseded/` are empty of actual specs.**
   `SPEC_DRIVEN_DEVELOPMENT.md` §2 step 1 says "write the stage's spec doc (in
   `plans/active/`) before any code/diagram," but Stage 01's work went straight to
   `docs/product/discovery/` and `docs/product/scqa/` without an intermediate
   `plans/active/01-discovery-scqa.md`. This is a **process deviation from the documented
   method**, not a content gap — either the method should be followed going forward, or
   `SPEC_DRIVEN_DEVELOPMENT.md` should be corrected to reflect that the prompt files
   themselves serve as the spec (making a separate `plans/active/` entry redundant for
   prompt-driven stages).
3. **`.claude/skills/skills.md` and `.claude/hooks/hooks.md` are empty indexes.** This is
   expected at this point (Stage 12 owns populating them) but is worth noting as a measured
   fact: zero governance enforcement exists in the repo today beyond documentation.
4. **No conflict found** between the reference-image repo pattern and V2's document
   lifecycle in the content produced so far (Stage 01's output landed cleanly in
   `docs/product/discovery/` and `docs/product/scqa/` as planned).

## 5. Current-state workflow sketch (as observed — how V3 has actually been built so far)

1. Stage 00: repo scaffolded twice — first as an ad-hoc structure, then replaced with the
   `.claude`-based canonical structure after the user supplied a reference image. The first
   pass's `knowledge/`, `evaluation/`, `runbooks/` folders survived the replacement but were
   never re-seeded (root cause of gap #1 above).
2. Stage 00 (continued): V2's 13 prompts were copied in by the user, reviewed for relevance,
   adapted (4 files modified, 9 unchanged beyond path remap), and 10 new prompts (14–23)
   authored for V3-only concerns.
3. Stage 01: Prompt 01 (Discovery) and Prompt 02 (SCQA/Minto) executed against real V2
   evidence, producing `discovery.md` and `scqa.md` (renamed from V2's original filenames
   for clarity, per explicit user request) plus DMAIC lenses and waste registers, mirrored
   to `workshop/participant-output/`.
4. Git workflow so far: work happens on the current stage's branch; downstream branches are
   fast-forwarded to keep them current; `main` is **only** updated on explicit instruction
   (established this session — a refinement to `SPEC_DRIVEN_DEVELOPMENT.md` §4's "merged to
   `main` only when exit criteria are met" rule, which did not originally specify that
   intermediate stage branches could be updated independently of `main`).

## 6. Fact / derivation / assumption / question register

| # | Item | Class |
|---|---|---|
| 1 | 184 files tracked in git as of this measurement | **Fact** |
| 2 | `knowledge/`, `evaluation/`, `runbooks/` have zero tracked files | **Fact** |
| 3 | `main` is one commit behind the stage branches | **Fact** |
| 4 | Only Stage 01 has real design content; Stages 02–21 are scaffold-only | **Fact** |
| 5 | The `plans/active/` gap is a process deviation rather than an intentional method change | **Derivation** — inferred from comparing `SPEC_DRIVEN_DEVELOPMENT.md`'s stated method to actual Stage 01 execution |
| 6 | Whether `plans/active/` should be retroactively populated for Stage 01, or the method documentation corrected instead | **Question** — open, see §7 |

## 7. Next-actions backlog (this stage's equivalent of Prompt 01's evidence acquisition backlog)

| ID | Item | Owner | Blocks | Priority |
|---|---|---|---|---|
| NAB-1 | Seed `knowledge/`, `evaluation/`, `runbooks/` with README stubs matching every other folder's convention | This stage | — | **Closed** (done this stage) |
| NAB-2 | Decide: does `SPEC_DRIVEN_DEVELOPMENT.md`'s `plans/active/` step apply to prompt-driven stages (01–19, which already have a spec in `prompts/`), or only to stages without a pre-written prompt (20, 21)? Update the method doc to match actual practice. | User / method owner | Stage 03 onward, so the same ambiguity doesn't repeat | Low-medium |
| NAB-3 | Carry forward V2's `knowledge/`, `evaluation/` reference content (32 knowledge docs, evaluation plan/fixtures/contracts) into the equivalent V3 folders if they are meant to be actively used, not just referenced from the V2 sibling directory | User (scope decision) | Stage 06 (DDD may need knowledge docs), Stage 14 (eval-ai-cache needs V2's evaluation plan as a floor) | Medium |

---

## Lean / DMAIC lens

See `dmaic_lens.md` (this folder) — thin, Measure-focused (Stage 02 is not a designated
full-DMAIC stage).
