# HITL Control Model — Named Accountable Approvers (EAB-3 closure)

**Status:** EAB-3 **closed**. Stage 16 (Governance & Control) expands this into the full
policy register (`policy_register.md` P-07/P-08/P-09); this document establishes the
accountable roles that were blocking DDD from `stable`. §7 is Stage 16's addition — the
remainder is unchanged from its original closure.

**Evidence basis: Fact.** Every role below is taken verbatim from V2's
`case/STAKEHOLDER_PACK.md`, which defines 15 stakeholders with explicit decision authority.
These were **not invented** — using the existing domain roles keeps V3 consistent with the
organization the case describes, and several of them already state the exact constraint V3
needs.

---

## 1. Why roles, not individuals

Accountability attaches to a **role**, not a person: individuals change, the accountable
authority persists, and an audit trail that names a role stays valid across staff turnover.
Individual people are bound to these roles at deployment time in the operating organization.
This is standard practice in GxP and is what ISO 42001 expects of an AI management system.

## 2. Approvers per workflow

### Workflow A — GxP Batch Review

| Level | Role | Authority (per `STAKEHOLDER_PACK.md`) |
|---|---|---|
| **Primary approver** | **EU Qualified Person (QP)** | "EU batch certification"; **"Final certification remains human-only"** |
| Escalation / policy | **Chief Quality Officer** | "Quality-system policy and risk acceptance" |
| **Explicitly NOT an approver** | Manufacturing VP | "Operations, **never independent batch release**" — recorded as a negative constraint so no future stage mistakes throughput ownership for release authority |

The QP's own mandate already states final certification is human-only, which is the exact
boundary ADR-004 enforces structurally. The system supports the QP's evidence review; it
never certifies.

### Workflow B — Pharmacovigilance Intake & Signal Support

| Level | Role | Authority |
|---|---|---|
| **Primary approver** | **Global Head of Pharmacovigilance** | "Safety-system performance"; **"Final safety decisions remain human-only"** |
| Medical escalation | **Chief Medical Officer** | "Clinical governance and escalation"; concern on record: "AI overreach into medical judgement" |
| Advisory veto | **Patient Safety Representative** | "Advisory veto through safety governance" |

The Global Head of PV's stated concern — "duplicate, multilingual and clock errors" — is
precisely what the PV-Intake Agent assists with, and their stated authority is precisely what
it must never assume.

### Workflow C — Supply-Shortage & Cold-Chain Planning

| Level | Role | Authority |
|---|---|---|
| **Primary approver** | **Supply Chain VP** | "Planning; **regulated execution needs approvals**" |
| **Co-approver where quality status is implicated** | **EU Qualified Person** or **Chief Quality Officer** | Quality status is not a supply decision |

Note the dual approval: the stakeholder pack explicitly limits the Supply Chain VP to
*planning*, with regulated execution requiring separate approval. Any option touching
quality status, cold-chain excursion disposition, or release therefore needs Quality
sign-off in addition. This is a real constraint the pack encodes, not an added formality.

## 3. Bounded-context owners (closing DDD §4's TBDs)

| Bounded context | Accountable owner |
|---|---|
| Batch Review | **Chief Quality Officer** (policy) / **EU Qualified Person** (per-batch decisions) |
| PV Intake | **Global Head of Pharmacovigilance** |
| Supply Planning | **Supply Chain VP**, with Quality co-approval as above |
| Evidence & Provenance | **Chief Quality Officer** — evidence authority is a quality-system concern |
| Governance & Oversight | **Chief Quality Officer** as AI-management-system owner, with **CISO** (security controls, incident response), **Data Protection Officer** (privacy risk acceptance and escalation) |
| Agent Orchestration (technical) | Engineering/Platform — no business decision authority |

## 4. Default-safe behavior (unchanged, now with a named owner)

HITL timeout results in **no action** — never auto-proceed. Escalation on timeout routes to
the escalation role named in §2 for that workflow. Silence is never approval.

## 5. Governance conflicts to design around

`STAKEHOLDER_PACK.md` names deliberate conflicts that directly affect this control model:

- **Quality vs. Manufacturing** disagree on whether speed or evidence completeness binds.
  The system must not become an instrument for resolving that conflict in either direction —
  it reports evidence state, it does not arbitrate priorities.
- **Global standardization vs. local jurisdictional authority.** Relevant to
  jurisdiction-local evidence (V2's `knowledge/` contains jurisdiction-scoped documents); the
  evidence layer must respect local authority rather than flattening it.
- **Privacy minimization vs. GxP preservation.** Affects trace retention (Stage 17) and
  compliance evidence (Stage 19) — the DPO and Chief Quality Officer have genuinely opposed
  incentives here, and the retention design must be explicitly agreed by both rather than
  chosen by engineering default.

## 6. Consequences of this closure

- **DDD moves `provisional` → `stable`** — EAB-3 was its stated blocker.
- ADR-005 and ADR-008 move `proposed` → `accepted` (they rested on DDD stability).
- ADR-006 moves `proposed` → `accepted` (nothing further blocked it).
- **ADR-007 stays `proposed`** — blocked on EAB-2 (air-gap), which is unrelated to this
  closure.
- **C4 stays `provisional`** — its container set includes the hosted dependencies (LangSmith,
  LLM provider) that EAB-2 governs.

## 7. Stage 16 addition — confirming the ladder durations against these roles

`failure_and_loop_guards.md` §5 set the four-tier timeout ladder (T0–T3) and durations,
explicitly deferring their *confirmation* with each accountable role to this stage. This
section closes that: **the durations are adopted as-is, unconfirmed with the live
organization** (no operating org exists yet to confirm against — the roles above are the
stakeholder pack's stated authorities, not contacted individuals). This is stated honestly:
"confirmed" here means *checked for consistency against each role's stated authority and
availability expectations in `case/STAKEHOLDER_PACK.md`*, not *signed off by a person*.

| Workflow | Ladder | Consistency check against this document's roles |
|---|---|---|
| Batch Review | 8bh / 16bh / 24bh | EU QP is a named, single-accountable role (§2) — a multi-day business-hours clock matches evidence review, not an urgent action. Escalation to CQO (§4 of `failure_and_loop_guards.md`) matches the CQO's stated "risk acceptance" authority in §2 above |
| PV Intake | 4h / 8h / 24h — wall clock | Matches §2's "final safety decisions remain human-only" — the short window exists so the system is never the reason a reporting clock is missed, consistent with the Global Head of PV's own stated concern about "clock errors" |
| Supply Planning | 8bh / 16bh (Quality leg only) / 24bh | Matches §2's dual-approval structure — the escalation applies only to the Quality co-approval leg because that is the only leg with an escalation role at all (§4 of `failure_and_loop_guards.md`); Supply Chain VP's leg has none, consistent with the stakeholder pack naming no role above it |

**Config, not code.** Per `failure_and_loop_guards.md` §5, these durations live in
`security/policies/` config (see `control_ownership.md`), not in graph code. Changing a
duration is a policy-register change with an audit entry (`escalation_override_log_design.md`
§3 covers the log shape for the *override* case; a duration change is a separate,
non-override policy edit and is out of this document's scope beyond noting it is **not** a
redeployment).

**Revisit trigger (new, T-11):** the first time this system operates against a real
organization, every role in §2 and every duration in this section must be re-confirmed against
an actual named Entra-group assignment and an actual approver's stated availability — this is
a design-time consistency check, not operational confirmation, and must not be mistaken for
one at Stage 20.

## 8. Stage 22 addition — severity/timer display, and what it deliberately is not

Two things were added to the AEGIS Control Center UI: a live "how overdue is this"
severity badge (1–4, colour-coded) on every pending run, and this document's own §7
ladder durations wired to actually compute it — both `services/integration/hitl_timer.py`
(read-time, recomputed on every request) and `hitl_route.py` (Batch Review's own state
machine, referenced but still not called by anything live — see below).

**What this closes.** Before this stage, §7's per-workflow ladder durations existed only
as design intent — no running code read them. `hitl_timer.py` now applies the *correct*
per-workflow ladder (Batch Review 8h/16h/24h, PV Intake's deliberately shorter 4h/8h/24h,
Supply Planning 8h/16h/24h) to every pending run's actual elapsed wait time, surfaced as a
badge in the Decision Queue and on the Decision Detail page. An earlier draft of this
feature used Batch Review's numbers for all six workflows before this section was
consulted — caught and fixed before merge, not caught after; recorded here so the
mistake and its correction are both on the record, not just the fix.

**What this does NOT close, stated plainly:**
- **No live scheduler.** `hitl_route.resolve_tier` (§7's actual escalation-ladder state
  machine, widening approver eligibility at T2) is still called nowhere outside its own
  test file. `hitl_timer.py` is a read-time, display-only computation — reaching severity
  4 changes a badge's colour, not who is authorized to decide the run.
  `user_store.approver_string_for` is completely unaffected.
- **No notification channel.** No email, Slack, webhook, or push exists in this build.
  Severity is only visible to someone who opens the app and looks.
- **The three Stage 21 workflows have no documented ladder.** `research_review`,
  `clinical_integrity`, and `regulatory_completeness` postdate this document; `hitl_timer.py`
  falls back to the Batch Review numbers for them as the closest analog, stated as an
  explicit assumption in its own module docstring, not a value derived from a stakeholder
  consultation the way §7's three original rows were.
- **Dev-only backdating aid.** `services/api/pending_queue.py::debug_backdate`, exposed
  only via `POST /api/debug/backdate/{run_id}` and only when
  `AEGIS_ENABLE_DEBUG_ENDPOINTS=1` is set, rewrites a real pending run's `created_at` so
  the severity tiers can be exercised without waiting real hours. It touches only that
  timestamp — never the run's findings, evidence, or audit trail — and is unreachable from
  any UI control or default configuration.

**Revisit trigger, extended:** the same T-11 trigger above applies to actually wiring
`resolve_tier` (or an equivalent) to a live clock, and to researching real ladder
durations for the three Stage 21 workflows, when this system next operates against a real
organization.
