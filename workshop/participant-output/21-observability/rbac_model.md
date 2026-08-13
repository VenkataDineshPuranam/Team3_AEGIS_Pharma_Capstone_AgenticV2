# RBAC Model — Stage 17

**Executes:** added to Stage 17 scope at the user's request (identified as a genuine gap: zero
prior mention of RBAC anywhere in `docs/`, `security/`, or `.claude/` before this stage).
**Consumes:** `c4_containers.md` (9 containers), ADR-008 (one graph per workflow, no cross-
graph calls), ADR-009 (Entra ID named as the identity platform), `policy_register.md` P-03
(cross-graph tool access), `hitl_control_model.md` (human approver roles)
**Artifact status:** `provisional` — design only, no Entra tenant exists to bind against

---

## 1. Why this wasn't already covered, precisely

Two things already existing were easy to mistake for RBAC, and are not:

- **`hitl_control_model.md`** names *who approves what* (EU QP, Global Head of PV, Supply Chain
  VP...). That is decision authority for a human sign-off step, not a system access-control
  model — it says nothing about which service identity may call which container.
- **P-03** (`policy_register.md`) checks that a graph run holds a credential for its own
  bounded-context MCP server. That is one boundary rule enforced by one hook, not a designed
  RBAC model with roles, scopes, and an assignment source of truth.

This document is the thing neither of those is: a role-based access model for **every actor
that can reach a container** — human or service — with Entra ID (ADR-009) as the single
identity platform for both, so there is one place role assignments live, not two.

## 2. Two planes, one platform

| Plane | Actors | Governs access to | Assignment source |
|---|---|---|---|
| **Human plane** | Named roles from `hitl_control_model.md` §2 (EU QP, Global Head of PV, Supply Chain VP, CQO, CMO, Patient Safety Rep, DPO, CISO) + operational roles this document adds (§3) | Web/Admin App views, HITL approval queue, dashboards, audit records, trace data | Entra ID group membership, checked live (same pattern as E2 in `failure_and_loop_guards.md` §5.3 — "current authorization at execution time," not at some earlier binding) |
| **Service plane** | One managed identity per container (§4) | Container-to-container calls, MCP tool servers, Redis, the audit store | Entra ID **managed identities** + Azure RBAC role assignments (ADR-009's platform), least-privilege, scoped per bounded context |

Both planes use the same identity platform so there is exactly one place — Entra ID — that a
Stage 19 compliance reviewer or a Stage 18 red-team checks for "who/what can reach this," not
a human-roles table plus a separate, informally-described service-credential scheme.

## 3. Human plane — roles this design adds beyond `hitl_control_model.md`

`hitl_control_model.md` covers *decision* authority. It does not cover *system* access — who
can view a trace, read an audit record, or see a dashboard. Those are new roles, named here for
the first time:

| Role | Can access | Cannot access | Basis |
|---|---|---|---|
| **Approver** (the roles in `hitl_control_model.md` §2) | Their own workflow's HITL queue, the evidence attached to a pending decision | Other workflows' queues (no cross-workflow approval authority was ever granted — inventing shared visibility here would create an authority path `hitl_control_model.md` never intended) | `hitl_control_model.md` §2 |
| **Compliance Reviewer** (Stage 19 consumer) | Audit store (read-only), redacted traces, `policy_register.md` | Live HITL queues (not an approval role), unredacted trace data | ISO 42001 audit-evidence requirement — needs read access without decision authority |
| **Platform Operator** (Engineering/Platform, `hitl_control_model.md` §3 "no business decision authority") | Dashboards, alert configuration, structural-cap/ceiling config values | Any HITL approval action, unredacted PII/PHI in traces, the ability to change a *policy* value (that's Governance & Oversight's role, not Platform's) | `hitl_control_model.md` §3 — this document makes explicit what "no business decision authority" excludes |
| **Governance & Oversight owner** (CQO/CISO/DPO, `hitl_control_model.md` §3) | Policy register values, escalation-role assignments, redaction rule content | — (broadest human role, matching their existing accountable-owner status) | `hitl_control_model.md` §3, `control_ownership.md` |

**Explicit negative constraint, carried forward:** Manufacturing VP remains excluded from every
plane and every role above, exactly as `hitl_control_model.md` §2 states for approval — this
document does not create a side door into observability data for a role the governance model
deliberately excludes from decision authority.

## 4. Service plane — one managed identity per container, scoped to its own bounded context

| Container | Managed identity | May call | May **not** call | Enforced by |
|---|---|---|---|---|
| Orchestrator API | `mi-orchestrator` | Its own workflow's MCP tool servers, Governance/Policy Engine, Redis, Audit store (write), LangSmith (write) | Another workflow's MCP tool servers (ADR-008) | P-03 credential check (pre-tool-call) + Azure RBAC role assignment scoped to that server only |
| Agent Workers | `mi-workers` | Same scope as its paired Orchestrator API identity, per workflow | Cross-workflow, same as above | Same |
| MCP Tool Servers (per bounded context) | `mi-mcp-<context>` (one per server, per `hooks.md`'s "one MCP server per bounded context" design) | Its own domain's read-only data source | Any write-capable brownfield integration (none exist, ADR-004 layer 2) | No write role assignment exists to grant — structurally absent, not merely unassigned |
| Governance/Policy Engine | `mi-governance` | Read policy config (`security/policies/`), write audit records for policy decisions | Nothing else — this identity has no reason to call any domain tool server | Least-privilege: the narrowest role set of any container, matching ADR-005's "independently versioned, independently deployed" isolation |
| Audit/Evidence Log Store | N/A (data store — the accessing identity is whichever container above holds a write role) | — | — | WORM/immutability policy (ADR-009) — even a holder of the write role cannot modify or delete an existing record |
| Redis Cache | N/A (data store) | — | — | Accessed only by Orchestrator API / Agent Workers identities, per-workflow key namespacing (Stage 15) |
| LangSmith | External | Receives redacted trace writes from `mi-orchestrator`/`mi-workers` only | — | API key scoped per environment, rotated via Key Vault (ADR-009) |
| Web/Admin App | `mi-web` | Orchestrator API (on behalf of the authenticated human user — delegated, not its own broad access) | Any container directly, bypassing the Orchestrator API | Standard on-behalf-of delegation; the app itself holds no domain data access of its own |

**The service plane is a direct restatement of ADR-008 in RBAC terms**, not a new architectural
decision: "one graph per workflow, zero cross-graph calls" becomes "one managed identity per
workflow-scoped container, zero role assignments crossing that scope." Where ADR-008 already
enforces this structurally (no edge exists in the graph), this section adds the platform-level
enforcement (no Azure role assignment exists either), so the same invariant holds even against
an access path the graph design didn't anticipate.

## 5. What this closes and what it doesn't

**Closes:** the RBAC gap identified when starting Stage 17 — there is now a named model for
every actor class reachable from `c4_containers.md`, mapped to the one identity platform ADR-
009 already committed to.

**Does not close (explicitly deferred, not hidden):**
- **No Entra tenant exists yet to bind these role definitions against** — this is a design,
  Stage 20 implements it. Status stays `provisional` until then.
- **Fine-grained data-row scoping** (e.g., can a PV approver see a Batch Review case's PII if
  the two happen to share a patient) is not addressed — this document scopes by *container and
  workflow*, not by *data row*. If Stage 13's `SensitiveSegment` access-group finding (ontology
  stage) requires row-level scoping beyond container boundaries, that is a follow-on design,
  named here as an open item rather than assumed covered.
- **Break-glass / emergency access** (e.g., CISO needs emergency read access outside normal
  role assignment during an incident) is not designed — Stage 18 (AI Security) is the more
  appropriate owner for that, since it is fundamentally a threat-response procedure.

## 6. Traceability

| RBAC element | Traces to |
|---|---|
| Human-plane approver roles | `hitl_control_model.md` §2 (unchanged, cited not restated) |
| Human-plane new roles (§3) | New at this stage — first time system access (not decision access) is modeled |
| Service-plane one-identity-per-container, zero cross-scope | ADR-008 |
| Identity platform choice (Entra ID) | ADR-009 |
| Write-role absence on MCP tool servers | ADR-004 layer 2 |
| Audit store immutability | ADR-009 (WORM), ADR-006 (separate store) |
