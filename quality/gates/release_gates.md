# Release Gates — Stage 14

**Executes:** `prompts/18_eval_ai_cache.md` §3 (Control), exit criterion "Release gates are
wired to block Stage 20 build sign-off on failure"
**Executable policy:** [`release_gates.py`](release_gates.py) (this directory) — a pure
function over grader results, verified against 63 real eval-dataset scenarios (`scorecard.md`)
**Artifact status:** `stable`

---

## 1. Gate-state vocabulary — consumed from `eval-ai-cache/`, not reinvented

Per NAB-4/trigger T-7, this stage must justify deriving rather than reusing already-seeded
material. It doesn't derive here: the gate-state vocabulary below is taken directly from
`eval-ai-cache/AI_FDE_Brownfield_Evals_Cursor_Runbook/14_Define_Eval_Gates.md`'s "Allowed gate
states" list.

| State | Meaning | Used where in this stage |
|---|---|---|
| `PASS` | Grader ran, condition satisfied | Most of the 63 scenarios |
| `FAIL` | Grader ran, condition violated | None remaining — all fixed this session (see `scorecard.md` §2) |
| `REVIEW` | Ambiguous, needs human judgement | Category 1 (business outcome) — human rubric |
| `NOT_APPLICABLE` | No automated grader exists for this category, by design | BO-01, BO-02 |
| `NOT_OBSERVABLE` | Would need a running system to observe | Not used this stage — everything here either ran against fixtures or was explicitly marked blocked |
| `THRESHOLD_NOT_DEFINED` | The check is real but the numeric threshold doesn't exist yet | LCD-04 (cost-per-task cap — U1 Unknown) |
| `BLOCKED_BY_ENVIRONMENT` | Cannot be scored until an external condition resolves | MSR-01 (ADR-009 LLM route unconfirmed) |

**Never calculate a naive average across dimensions** — same rule the runbook states and V2's
own `release_gates.py` implements ("Hard-gate failures must not be averaged away"). This
programme's `release_gates.py` follows the identical shape: any single hard-gate failure blocks,
independent of how many other categories passed.

## 2. Hard / threshold / operational split

Per the runbook's own taxonomy (`14_Define_Eval_Gates.md`), consumed rather than re-derived:

| Class | This programme's gates | Blocks Stage 20 build sign-off? |
|---|---|---|
| **Hard gates** | `G-SCHEMA_FAILURE`, `G-FABRICATED_OR_UNCITED_FACT`, `G-EVIDENCE_AUTHORITY_VIOLATION`, `G-PROHIBITED_ACTION`, `G-FAIL_OPEN_VIOLATION`, `G-STRUCTURAL_CAP_EXCEEDED`, `G-AUDIT_TRAIL_INCOMPLETE`, `G-CACHE_STALE_SERVE` | **Yes, always** |
| **Threshold gates** | Cost-per-task cap (currently `THRESHOLD_NOT_DEFINED`), cache hit rate (N/A, no cache), latency budget (Unknown, U2) | Only once the threshold exists — cannot block on an undefined number |
| **Operational gates** | Business-outcome rubric score, HITL override rate | `REVIEW`-gated — needs a human decision, not a boolean |

## 3. Gate-to-source traceability

Every gate ID traces to a specific ADR, DDD invariant, or Stage 09-13 artifact — not invented
for this document:

| Gate | Source | Grader |
|---|---|---|
| `G-SCHEMA_FAILURE` | `packages/contracts/tool_contracts/*.schema.json` (Stage 11) | `schema_grader.py` |
| `G-FABRICATED_OR_UNCITED_FACT` | DDD `domain_model.md` §12 (every output must carry evidence citations) | `evidence_authority_grader.py:grade_evidence_fidelity` |
| `G-EVIDENCE_AUTHORITY_VIOLATION` | ADR-003 | `evidence_authority_grader.py:grade_authority` |
| `G-PROHIBITED_ACTION` | ADR-004 | `prohibited_action_grader.py` |
| `G-FAIL_OPEN_VIOLATION` | ADR-005, BC-3 | `security_grader.py:grade_fail_closed` |
| `G-STRUCTURAL_CAP_EXCEEDED` | `failure_and_loop_guards.md` G1-G8 | `loop_guard_grader.py` |
| `G-AUDIT_TRAIL_INCOMPLETE` | `langgraph_design.md` node `finalize` | `audit_trail_grader.py` |
| `G-MISSING_SUBGROUP_EVIDENCE` | EVALUATION_PLAN.md #10 (V2, verified), ported pattern | `subgroup_grader.py` |
| `G-CACHE_STALE_SERVE` | ADR-003 guardrail (register row D5/I1) | `cache_correctness_grader.py` |
| `G-UNREPRODUCIBLE_OR_BLOCKED` | Trajectory/critic-routing correctness (incl. the `PROHIBITION_ADJACENT` regression) | `trajectory_grader.py` |

## 4. Why this gate set is not a copy of V2's ten gates

V2's `submission/evaluation/policies/release_gates.py` has ten gates matching its own
`EVALUATION_PLAN.md` §"Release gates" list verbatim. This programme's gates above are
**independently re-derived from our own ADRs and DDD invariants**, per ADR-002's standing rule
(no code reuse; behaviour independently derived, not assumed to match). Where the underlying
*concept* is the same (schema failure, stale authorization, prohibited action), the specific
*rule* is sourced from our own contracts — e.g. `G-PROHIBITED_ACTION`'s banned-field list is
copied from `packages/contracts/tool_contracts/*.schema.json`, not from V2's
`_BANNED_BATCH_READINESS` set (verified different: V2's set includes `"reprocessed"`,
`"relabeled"` as batch statuses; ours is field-presence-based on the response object, a
different mechanism entirely, per ADR-004's schema-absence-first design).

## 5. Gate result on this stage's own eval dataset

See `scorecard.md` for the full run. Summary: **zero hard-gate blocks** across 63 scenarios.
This is expected and correct — the eval dataset's adversarial cases are constructed so the
*grader* catches the bad condition (grader returns `pass: False` on purpose), which is scored
as the scenario passing its *test*, not as a gate block on a real system (none exists to block
yet). The distinction matters and is kept explicit in `scorecard.md` §1.
