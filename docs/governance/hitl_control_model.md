# HITL Control Model — Named Accountable Approvers (EAB-3 closure)

**Status:** EAB-3 **closed**. Stage 16 (Governance & Control) will expand this into the full
policy register; this document establishes the accountable roles that were blocking DDD from
`stable`.

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
