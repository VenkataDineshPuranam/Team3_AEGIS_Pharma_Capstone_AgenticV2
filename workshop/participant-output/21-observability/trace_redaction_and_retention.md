# Trace Redaction & Retention — Stage 17

**Executes:** `prompts/21_observability.md` §4
**Consumes:** BC-8 ("redaction rules written before the first trace"), ADR-006, `hooks.md`'s
redaction row (post-tool-call / pre-checkpoint), `memory_design.md` §4–5, `policy_register.md`
P-10
**Artifact status:** `provisional` — ruleset defined here for the first time; owner (DPO + CQO
jointly, per `hitl_control_model.md` §5) has not yet signed off, since no such org exists to
sign off yet

---

## 1. This is the ruleset `hooks.md` §4 named as owed to this stage

`hooks.md` stated the redaction *binding point* (post-tool-call / pre-checkpoint hook) is
`stable`, but explicitly deferred the *ruleset content* to Stage 17. This document is that
content — checked, per §7 below, against `policy_register.md` P-10 before being treated as
final.

## 2. What gets redacted, mechanically — never a model judgment call

Per `hooks.md`'s existing invariant ("redaction rules are applied mechanically... not left to
the model to decide what's sensitive"), every rule below is a deterministic field-level or
pattern-level rule, not an LLM-assisted redaction pass (an LLM redacting PII is itself a
generation step that could fail exactly the way it's meant to prevent).

| Category | Rule | Applies to |
|---|---|---|
| **Approver personal identity** | Strip entirely; retain role + role-assignment ID only | Every span/record touching `hitl_route`, `hitl_interrupt`, `HumanOverrideRecorded` |
| **Guard-blocked draft text** | Strip entirely; retain reason code, prohibition class, SHA-256 hash | `prohibited_action_guard` spans, `ProhibitedActionBlocked` audit records |
| **Retrieved evidence full text** | Strip; retain item ID, authority status, jurisdiction tag | `tool.evidence_retrieve` spans |
| **PV case content (PII/PHI: patient identifiers, free-text case narrative)** | Field-level strip before span write; retain case ID, evidence IDs, status | `pv_intake` graph spans (once built) |
| **`SensitiveSegment` items (Stage 13 finding — pregnancy/minor case segments)** | Access-group check enforced *before* retrieval (evidence layer), and any item that reaches a span carries no segment content, only its `access_group` tag | Any span touching evidence with a `SensitiveSegment` classification |
| **Credentials, tokens, connection strings** | N/A — never present in state to begin with (`memory_design.md` §4); nothing to redact because nothing to strip from |
| **Raw request/response bodies** | Not traced at all (§2 of `tracing_design.md`); structured fields only | All spans |

## 3. Where redaction runs — one path per sink, not two

Per `memory_design.md` §4, redaction applies once, at the write boundary, for **both** sinks:

```
Node/hook produces raw span data
        │
        ▼
  Redaction rules (this document, §2) applied mechanically
        │
        ├──► LangSmith (trace)
        └──► Audit store (compliance record, where applicable)
```

**One redaction implementation, two destinations** — not a LangSmith-specific rule set and a
separate audit-store rule set that could drift apart. This directly satisfies the exit
criterion "trace redaction is verified against the governance policy register" by construction:
there is exactly one place to check, not two.

## 4. Retention — structure fixed here, duration still open (unchanged from Stage 10)

`memory_design.md` §5 already fixed the retention *structure* and left *durations* open,
pending the DPO/CQO agreement `hitl_control_model.md` §5 requires. This stage does not
override that — it restates it as the retention posture this design commits to, so Stage 19
inherits a structural decision, not a blank page:

| Store | Structure | Duration |
|---|---|---|
| Audit store | Immutable, WORM (ADR-009) | **Open** — ≥ GxP requirement, DPO/CQO joint decision |
| Traces (LangSmith + OTel backend) | Redacted per §2, append-only | **Open** — expected shorter than audit; DPO/CQO joint decision |
| Checkpoints | Deleted after terminal state + short resumption window | **Open** — window TBD |

**This design adds one retention-adjacent rule that is not duration-dependent:** a
guard-blocked draft's SHA-256 hash has no independent retention question — it retains exactly
as long as the record it's embedded in (`ProhibitedActionBlocked`), never separately, since a
hash with no surrounding context has no compliance value on its own.

## 5. Privacy-minimization vs. GxP-preservation — restated, not re-litigated

`hitl_control_model.md` §5 already named this as a genuine, unresolved tension between the
DPO's and CQO's stated interests. This document does not resolve it (durations stay open, §4)
but does narrow *what* is in tension: because redaction already strips personal identity and
free-text PII at the write boundary (§2), the retention-duration question is about **how long
to keep the redacted, structured record** — not "how long to keep raw PII," which this design
never writes anywhere to begin with. That reframing is a real narrowing of the Stage 19
decision, not a resolution of it.

## 6. Verified against `policy_register.md` P-10

| P-10 requirement | Met by |
|---|---|
| Redact before any write to LangSmith or audit store | §3 (single redaction path, both sinks) |
| Discard the text of a guard-blocked draft; keep reason code, prohibition class, hash | §2 row 2 |

P-10's status in `policy_register.md` moves from "content not written" to **content specified
here** — its enforcement point (the hook) was already `stable`; this document is what closes
the "not fully specified until Stage 16... Stage 16 adds policy content to load, not new hook
bindings" forward reference `hooks.md` §4 made (the ruleset landed at Stage 17, one stage later
than that forward reference anticipated, matching the actual Wave 2 stage order).

## 7. What is not yet covered

- **PV/Supply-specific redaction rules beyond the general PII/PHI category** — `provisional`,
  same status as the PV/Supply graphs themselves (RR-2).
- **Actual DPO/CQO sign-off** — cannot happen before Stage 19 or before an operating
  organization exists; this document is the technical proposal that sign-off will be checked
  against, not the sign-off itself.
