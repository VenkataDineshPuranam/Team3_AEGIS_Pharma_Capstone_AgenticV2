# Domain Model — Stage 02 (DDD)

**Executes:** `prompts/04_ddd.md`
**Builds on:** `docs/product/discovery/discovery.md` (Stage 01), `docs/product/scqa/scqa.md` (Stage 01)
**Artifact status: `stable`** (upgraded from `provisional` when EAB-3 closed)

**Upgrade note:** this model was `provisional` because EAB-3 — accountable owners and HITL
role definitions — was open. **EAB-3 is now closed** (see
[`docs/governance/hitl_control_model.md`](../../governance/hitl_control_model.md)): the
accountable roles were taken verbatim from V1's `case/STAKEHOLDER_PACK.md`, which already
defines 15 stakeholders with explicit decision authority — including the EU Qualified
Person, Global Head of Pharmacovigilance, and Supply Chain VP, whose stated authorities map
exactly onto the three workflows. Owners below are no longer TBD. The design principle
(rules + HITL over autonomous AI) is retained on merit, not merely as provisional caution.

---

## Domain foundation

### 1. Frame business problem (domain terms)

NovaCura Therapeutics (the fictional organization in V1's `case/INTEGRATED_CASE.md`) needs
three governed decision-support capabilities — GxP batch-review evidence reconciliation,
pharmacovigilance case-intake/signal support, and bounded supply-shortage/cold-chain
planning — delivered as a multi-agent system instead of a single-shot app, **without**
expanding what the system is authorized to decide. The domain problem is not "what should
the AI decide" (nothing new — the system was always decision-support only) but "how do we
structure bounded contexts, agent responsibilities, and authority boundaries so that
splitting one governed decision into multiple agent turns cannot accidentally produce an
outcome a single-shot design could never have produced" (the H5 risk from
`docs/product/discovery/discovery.md` §9).

### 2. Domain & subdomains

**Core subdomains** (the business capabilities the system exists to deliver):
- **GxP Batch Review** — reconcile batch genealogy, lab results, environmental monitoring,
  deviations, CAPA, change control, validation state, supplier evidence, release-packet
  completeness (`case/INTEGRATED_CASE.md` Workflow A).
- **Pharmacovigilance Intake & Signal Support** — intake, duplicate detection, terminology
  normalization, source authority, reporting-clock reconstruction, listedness evidence,
  product-quality linkage, multilingual review (Workflow B).
- **Supply-Shortage & Cold-Chain Option Planning** — traceable options from inventory,
  quality status, market authorization, trial demand, compassionate-use constraints,
  cold-chain evidence, CMO capacity, transport, allocation policy (Workflow C).

**Supporting subdomains** (necessary, not the reason the system exists, shared across all
three core contexts):
- **Evidence & Provenance** — evidence authority, temporal applicability, provenance,
  conflict/supersession resolution (V1's `knowledge/` authority states — `approved`,
  `superseded`, `untrusted`, `draft`, jurisdiction-local — are the concrete evidence this
  subdomain must reason over, per V1 `CLAUDE.md`).
- **Governance & Human Oversight** — HITL routing, prohibited-terminal-action enforcement,
  audit trail, the "required operating properties" named in `case/INTEGRATED_CASE.md` §5
  (purpose limitation, least privilege, current authorization, abstention, human review,
  idempotency, bounded steps, cost/token budgets, checkpointing, rollback, kill switch,
  degraded mode, auditability, AI-disabled continuity).

**Generic subdomains** (commodity technical capability, not pharma-specific):
- **Agent Orchestration Runtime** — LangGraph graph execution, shared state, checkpointing.
- **Observability** — LangSmith/OTel tracing.
- **Caching** — Redis response cache.

### 3. Ubiquitous language

| Term | Meaning | Status |
|---|---|---|
| Decision support | The system's only mode — proposes, flags, reconciles; never executes a terminal action | Stable (V1-inherited, non-negotiable) |
| Prohibited terminal action | Per workflow: release/reject/reprocess/relabel/recall (A); final seriousness/causality/expectedness/reportability/signal-confirmation decision (B); change inventory status/reserve/allocate/release/recall (C) — verbatim from `case/INTEGRATED_CASE.md` §4 | Stable |
| Evidence authority | Which source may assert a fact; V1 encodes this as document status (`approved`/`superseded`/`untrusted`/`draft`) rather than a binary trust flag | Stable |
| Abstention | The system declines to answer/act when identity, unit, time, terminology, jurisdiction, source authority, or evidence completeness cannot be resolved (`CLAUDE.md` guardrails) | Stable |
| Agent | **(V2, new term)** a bounded, named unit of LangGraph-orchestrated reasoning with a stated authority limit and tool set — not synonymous with V1's `.claude/agents/` (which are engineering-time helper agents like `evidence-reviewer`, distinct from the runtime domain agents this system executes) | **Unresolved — flagged.** The name "agent" is overloaded between V1's build-time Claude Code agents and V2's runtime domain agents. Resolution: this document uses "domain agent" for the V2 runtime concept throughout, and "Claude Code agent" when referring to V1's build-time helpers, to avoid collision. |
| Authority limit | The explicit boundary of what a domain agent may propose vs. what requires human sign-off | **(V2, new term)** — provisional, this document is where it's first defined (§10 below) |
| Bounded context crossing | A handoff between two domain agents whose bounded contexts differ, requiring an explicit contract rather than shared understanding | **(V2, new term)** |

### 4. Bounded contexts

| Context | Owner (business) | Decisions it owns |
|---|---|---|
| **Batch Review** | **Chief Quality Officer** (policy) / **EU Qualified Person** (per-batch) | Evidence reconciliation completeness, deviation/gap flagging — **not** release/reject |
| **PV Intake** | **Global Head of Pharmacovigilance** | Duplicate detection, terminology normalization, signal triage/prioritization — **not** causality/seriousness/reportability |
| **Supply Planning** | **Supply Chain VP** (planning only; Quality co-approval for quality status) | Option generation, constraint flagging — **not** allocation/shipment/recall |
| **Evidence & Provenance** | Platform/shared (cross-functional) | Evidence authority resolution, conflict/supersession rules — an **upstream service** to the three core contexts, not a decision-owner itself |
| **Governance & Oversight** | **Chief Quality Officer** (AI-MS owner), **CISO**, **Data Protection Officer** | HITL routing rules, prohibited-action enforcement, audit trail requirements — enforces boundaries on all three core contexts |
| **Agent Orchestration** (generic/technical) | Engineering/Platform | Graph execution, state management — no business decisions, hosts the above |

**All owners are now named** (EAB-3 closed). Accountability attaches to the **role**, not an
individual — roles persist across staff turnover and keep the audit trail valid, which is
standard GxP practice and what ISO 42001 expects. See
[`hitl_control_model.md`](../../governance/hitl_control_model.md) §1.

### 5. Context map

```
                    ┌─────────────────────────┐
                    │  Governance & Oversight   │  (upstream to all — open-host
                    │  (policy, HITL, audit)     │   service / published language)
                    └────────────┬────────────┘
                                 │ policy contract
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │ Batch Review   │  │  PV Intake     │  │ Supply Planning│   (core, peer contexts —
      │  (core)        │  │  (core)        │  │  (core)        │    no direct coupling)
      └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                    ┌─────────────────────────┐
                    │  Evidence & Provenance   │  (upstream, shared kernel —
                    │  (authority, conflicts)   │   conformist: core contexts accept
                    └────────────┬────────────┘   its evidence contract as-is)
                                 ▼
                    ┌─────────────────────────┐
                    │   Agent Orchestration     │  (generic/technical, hosts
                    │   (LangGraph runtime)      │   all of the above at runtime)
                    └─────────────────────────┘
```

Relationship types (DDD vocabulary):
- **Governance & Oversight → {Batch Review, PV Intake, Supply Planning, Agent
  Orchestration}**: open-host service / published language — Governance publishes a policy
  contract (prohibited-action list, HITL trigger rules) that every other context conforms
  to. This is deliberately **not** a shared kernel — Governance's policy contract is versioned
  and owned independently so it cannot be silently weakened by a core context's local needs.
- **Evidence & Provenance → {Batch Review, PV Intake, Supply Planning}**: shared kernel —
  all three core contexts consume the identical evidence-authority model; a conformist
  relationship (core contexts do not get their own evidence semantics).
- **{Batch Review, PV Intake, Supply Planning}**: peer, no direct coupling — a batch-review
  domain agent never calls a PV-intake domain agent directly. Any cross-workflow need routes
  through Evidence & Provenance or Governance, never context-to-context.
- **Agent Orchestration**: technical host for all contexts' runtime agents — not a business
  decision-owner, so it has no upstream/downstream business relationship, only a hosting one.

### 6. Domain events (event storming, abbreviated to material events)

| Event | Context | Notes |
|---|---|---|
| `EvidenceCited` | Evidence & Provenance | Fired whenever any domain agent output references a source; carries authority status |
| `EvidenceConflictDetected` | Evidence & Provenance | Two sources disagree; must not be silently resolved (per `CLAUDE.md` guardrails) |
| `BatchEvidenceReconciled` | Batch Review | Reconciliation complete; **never** co-occurs with a release/reject recommendation |
| `DeviationFlagged` | Batch Review | |
| `PVCaseIntakeReceived` | PV Intake | |
| `DuplicateSuspected` | PV Intake | |
| `SignalTriaged` | PV Intake | Prioritization only — **never** a causality/seriousness/reportability determination |
| `ShortageOptionsGenerated` | Supply Planning | Options are non-executing by construction |
| `ColdChainConstraintFlagged` | Supply Planning | |
| `ProhibitedActionBlocked` | Governance & Oversight | Fired when a hook/policy check intercepts an attempted prohibited action — **this event existing at all is the control signal**; it should be rare, and its absence over time is not proof of safety (could mean no attempts, or could mean the block isn't wired — see Stage 16/18) |
| `HumanOverrideRecorded` | Governance & Oversight | Every HITL decision, approve or reject, logged |
| `AgentAuthorityExceeded` | Governance & Oversight | **Defect event** — should never fire in a correctly governed system; its presence in any trace is a Stage 18 (security) and Stage 12 (assurance) finding, not routine telemetry |

### 7. Entities, value objects, aggregates & invariants

| Element | Type | Invariant |
|---|---|---|
| `Batch` | Aggregate root | Cannot carry a `release_recommended` or `reject_recommended` field — the aggregate's schema itself must make the prohibited action unrepresentable, not merely unrecommended |
| `PVCase` | Aggregate root | Duplicate-check (`DuplicateSuspected` evaluation) must complete before `SignalTriaged` can fire |
| `ShortageOption` | Value object, immutable | Always paired with its constraint set; never carries an `allocated_quantity` field — allocation is out of this system's aggregate model entirely, not just unrecommended |
| `EvidenceItem` | Value object | Carries source, authority status (`approved`/`superseded`/`untrusted`/`draft`/jurisdiction-local per V1's `knowledge/` model), effective date, and a supersession pointer if applicable |
| `AgentRun` | Aggregate root (**V2, new**) | One per domain-agent execution; carries authority-limit reference, tool calls made, evidence cited, and — if applicable — the `HumanOverrideRecorded` event it triggered. This aggregate is what Stage 17 (observability) and Stage 12 (assurance) query. |

---

## Gen AI boundary design

### 8. Rules vs. AI reasoning

**Deterministic rules (never delegated to AI judgment):**
- Prohibited-action blocking (the schema-level unrepresentability above, plus a runtime hook — Stage 16).
- Evidence authority resolution — a lookup against document status, not a judgment call.
  **Corrected at Stage 04 by [ADR-003](../../adr/ADR-003-evidence-authority-deterministic-gate.md):**
  this section originally said "untrusted excluded entirely; superseded flagged, not
  silently substituted." Verification against V1's `submission/evaluation/graders/authority_grader.py`
  (`_MUST_NOT_CITE = {"untrusted", "superseded"}`) proved that wrong — **`superseded` is
  non-citable, exactly like `untrusted`**, and both must be filtered at the retrieval
  boundary so they never enter an agent's context. Retrieved content may also never alter
  its own authority (the grader independently fails any response where an embedded
  instruction was followed).
- Duplicate-detection *thresholds* (if V1's PV duplicate logic is numeric/rule-based —
  unconfirmed this pass; flagged for Stage 06/07 to verify against V1's actual grader code,
  e.g. `submission/evaluation/graders/temporal_unit_grader.py`).

**AI reasoning (appropriately probabilistic):**
- Natural-language synthesis of reconciled evidence into a human-readable summary.
- Ranking/prioritization *within* a rule-bounded candidate set (e.g., ranking shortage
  options that already passed the deterministic constraint filter).
- Free-text terminology normalization suggestions (PV context) — always presented as a
  suggestion with confidence, never silently applied.

### 9. RAG design (from DDD artefacts)

Retrieval is scoped **per bounded context**, not global: a Batch Review domain agent
retrieves only from Batch Review's evidence scope (never PV or Supply knowledge), routed
through the Evidence & Provenance context's semantic layer (Stage 13 dependency — this
document specifies the *requirement*, not the implementation). Out of retrieval scope by
design: any document marked `untrusted` (V1's poisoned-trap documents, e.g. the pattern
represented by `FAKE_PV_EXPEDITED_RULE`/`MALICIOUS_SUPPLIER_DEVIATION` in V1's `knowledge/`)
must never enter a domain agent's context window, full stop — this is a retrieval-time
filter, not a "the AI should recognize it's untrustworthy" instruction.

### 10. Agent responsibilities (V2, named agents)

| Domain agent | Bounded context owned | Tools it may call | Authority limit | Stop/escalation condition |
|---|---|---|---|---|
| **Batch-Review Agent** | Batch Review | Evidence retrieval (scoped), reconciliation tool | May propose evidence reconciliation, flag deviations/gaps | Escalates to HITL on any conflict it cannot resolve via deterministic rules, or any output that would resemble a release/reject signal even implicitly |
| **PV-Intake Agent** | PV Intake | Evidence retrieval (scoped), duplicate-check tool, terminology-normalization tool | May triage/prioritize signals, suggest normalization | Escalates on any output touching causality/seriousness/expectedness/reportability — these fields must not exist in this agent's output schema at all |
| **Supply-Planning Agent** | Supply Planning | Evidence retrieval (scoped), option-generation tool | May generate ranked, non-executing options | Escalates on any request that would require writing an allocation/reservation — this agent has **no tool capable of that write**, by design (Stage 11 tool-contract requirement, not just an instruction) |
| **Critic/Verifier Agent** | Governance & Oversight (cross-cutting) | Read-only access to any domain agent's proposed output | Checks output against the prohibited-action schema constraint and evidence-citation completeness before it reaches a human | Never itself modifies domain output — only approves-for-human-review or rejects-back-to-domain-agent |

**Explicitly rejected from this design:** a single generalist agent handling all three
workflows. Reason: each workflow's prohibited-action boundary is different and
domain-specific (see `case/INTEGRATED_CASE.md` §4's three distinct prohibition lists); a
generalist agent would need to hold all three boundaries in one prompt/context, which is
exactly the kind of authority-blurring the SCQA Answer's point 2 warns against
(`docs/product/scqa/scqa.md`).

**Bounded-context crossings (explicit, per prompt requirement):** every domain agent's
output crosses into the Governance & Oversight context when it reaches the Critic/Verifier
Agent. This crossing uses a common `DecisionSupportOutput` contract (Stage 08 §I2 will
formalize the schema) so the Critic/Verifier never needs to understand batch-review-specific
or PV-specific language — only the common contract fields (evidence citations, confidence,
abstention flag, prohibited-action-adjacent flag).

### 11. HITL & decision ownership

| Workflow | Named approver role | Escalation trigger |
|---|---|---|
| Batch Review | **EU Qualified Person** (escalation: Chief Quality Officer) | Any deviation/gap the agent cannot fully reconcile; any output flagged by the Critic/Verifier |
| PV Intake | **Global Head of Pharmacovigilance** (escalation: Chief Medical Officer) | Any case touching causality/seriousness/reportability by definition (100% of PV determinations, since the agent structurally cannot make them) |
| Supply Planning | **Supply Chain VP** + Quality co-approver where quality status is implicated | Any option set presented for consideration (100% — options are never self-executing) |

Default-safe behavior on HITL timeout: **no action taken, not "proceed with AI
recommendation"** — silence from a human reviewer must never be treated as approval. This
is a Stage 16 (governance) requirement recorded here as a domain-level constraint.

### 12. Evidence & audit trail

Every domain agent output must carry: evidence citations (from Evidence & Provenance,
including source authority status), a confidence/abstention field, and an `AgentRun` record
(LangSmith trace ID) satisfying both V1's evidence standard
(`requirements/SUBMISSION_EVIDENCE_STANDARD.md`, not re-read this pass but named as the
inherited floor) and V2's new compliance requirements (Stage 19).

### 13. Evaluation using DDD vocabulary

Eval cases (Stage 14) should be phrased in this document's vocabulary, e.g.:
- "A `BatchEvidenceReconciled` event must never co-occur with any release/reject signal in
  the same `AgentRun`."
- "Every `SignalTriaged` event's `AgentRun` must show a prior `DuplicateSuspected`
  evaluation."
- "No `ShortageOption` value object in any output may contain an `allocated_quantity`-shaped
  field."
- "Any `AgentAuthorityExceeded` event in a trace is an automatic Stage 14 release-gate
  failure."

---

## Governed path

### 14. Minimum governed workflow

One domain agent + its scoped evidence retrieval + the Critic/Verifier + a named HITL gate,
per workflow — **no cross-workflow agent chaining in the first governed slice.** This
directly implements the SCQA Answer's sequencing principle: prove the narrowest agentic
slice is safe before composing agents further.

### 15. Pilot / refine notes

Recommend piloting **Batch Review first** — it has the strongest evidence base of the three
per Stage 01's sufficiency scoring (`discovery.md` §10: "Evidence… Strong") and the most
mature V1 grader coverage (`temporal_unit_grader.py`, `authority_grader.py` both appear
batch/evidence-oriented from their names). What would change this model: EAB-3 resolution
(real HITL owners), and any evidence from a Batch Review pilot that the Critic/Verifier
contract is too coarse or too strict.

### 16. Production readiness concerns (domain view)

Not production-ready: no runtime enforcement yet exists for any of the schema-level
"unrepresentable prohibited action" invariants described above (Stage 10–20 work). Domain
ownership **is** now assigned (EAB-3 closed, §4/§11), which is what allowed this artifact to
reach `stable`. Remaining gap to production is implementation and its evidence, not
governance ambiguity.

---

## Exit criteria checklist

- [x] Artifact status (`stable`) stated with reason; upgraded on EAB-3 closure.
- [x] Ubiquitous language and bounded contexts explicit; one unresolved term flagged
      ("agent" — resolved by using "domain agent" vs "Claude Code agent" throughout).
- [x] Rules vs AI vs HITL boundaries written down (§8, §11).
- [x] AI autonomy minimized on merit — every domain agent is
      structurally blocked (schema/tool-capability level) from its workflow's prohibited
      action, not just instructed not to attempt it.
- [x] RAG/agent responsibilities map to domain artefacts (bounded contexts), not tech
      fashion.
- [x] Domain organized around business capability (batch review / PV / supply), not
      technical layers or dataset names.
- [x] Full `dmaic_lens.md` and updated waste registers complete (this folder).
