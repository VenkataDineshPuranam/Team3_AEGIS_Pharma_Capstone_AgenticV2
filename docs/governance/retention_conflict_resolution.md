# Retention Conflict Resolution — Stage 21 gap-closure (INJ-035, INJ-061)

**Executes:** closes two V2-inherited injects that are the same underlying rule applied
at two granularities:
- **INJ-035** (D05, general): legal hold, GxP retention, and privacy deletion obligations
  pointing to different actions for the same record.
- **INJ-061** (D09, PV-specific): a data-subject deletion request (DSAR) landing on data
  that may need preservation for trial/pharmacovigilance integrity — the identical
  conflict, scoped to a PV case record specifically.

This is deliberately a governance document, not a batch-reconciliation fixture. A
retention conflict is not a completeness question about a specific batch's evidence — it
is a standing rule about what AEGIS's own records (audit entries, retrieved evidence,
cached responses) must do when three real legal obligations disagree. Representing it as
a reconciliation-tool finding would misfile it: no batch reconciliation category asks
"should this record be deleted," and none should, per the same ADR-004 reasoning that
keeps disposition decisions out of every tool's output schema.

## The conflict, precisely

Three obligations can independently apply to the same record:

1. **GxP retention** — batch, PV, and supply records must be retained for the regulatory
   minimum period (product-dependent; commonly the longer of local law or product
   lifecycle plus a fixed tail).
2. **Legal hold** — litigation or an active regulatory inquiry can require preserving a
   specific record past its normal retention period, indefinitely, until released.
3. **Privacy deletion** — a data-subject deletion request (GDPR Art. 17 or equivalent)
   can require erasing personal data within a bounded time, subject to the exemptions the
   same regulation grants for legal-obligation and legal-claims purposes.

These are not symmetric. GxP retention and legal hold are both *preservation*
obligations; privacy deletion is an *erasure* obligation that already carries a
legal-obligation exemption in the regulations that create it (GDPR Art. 17(3)(b)/(e)).

## The rule this system applies

**Preservation wins whenever it is grounded in an active legal or regulatory obligation.**
A privacy deletion request does not erase a record that GxP retention or legal hold
requires AEGIS to keep — the applicable privacy regulation's own exemption is what makes
this lawful, not a judgment call made by this system. Concretely:

1. `services/integration/audit_store.py`'s WORM design already enforces the preservation
   half structurally — there is no `UPDATE`/`DELETE` function anywhere in that module, so
   an audit record cannot be erased by *any* code path in this system regardless of which
   obligation is cited, closing the failure mode where a deletion request could be
   fulfilled by mistake.
2. A privacy deletion request touching a record inside an active retention or legal-hold
   period is out of scope for AEGIS's own database entirely — the audit store holds no
   personal data by design (`packages/observability/trace_redaction_and_retention.md`
   §2's redaction rule), and the retrieved-evidence corpus (`knowledge/`) is policy/
   reference material, not personal data. The conflict this inject describes therefore
   applies to the *upstream systems* (MES, safety database, CRM) AEGIS reads evidence
   from — this system's job is to never become a second place the same conflict has to be
   resolved.
3. Where a future capability *would* introduce personal data into a durable AEGIS record
   (e.g. a PV case narrative retained beyond a single run), the resolution above still
   applies: preservation obligations are checked and satisfied before any deletion path
   is built, not after.

## What this closes, honestly

This is a real, reasoned rule — not a technical control that can fail a test the way a
reconciliation fixture can. Its correctness is verified by:
- `services/integration/audit_store.py`'s WORM property (no UPDATE/DELETE function
  exists — checked structurally by `tests/unit/governance/test_audit_read_layer.py::test_read_layer_adds_no_mutating_function`).
- `packages/observability/trace_redaction_and_retention.md`'s existing redaction rule,
  which is what keeps personal data out of the audit store in the first place.

Owner: Compliance Reviewer (`docs/governance/hitl_control_model.md` §3). Any future
feature that would let AEGIS hold personal data durably must re-open this document before
merging, not treat retention/hold/deletion as solved by inertia.
