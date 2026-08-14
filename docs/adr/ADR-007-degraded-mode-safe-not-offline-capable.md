# ADR-007 — V3 is "degraded-mode-safe," not "offline-capable"

**Status:** `accepted` — sponsor confirmed cloud-connected operation is acceptable
(EAB-2 closed). The reframing below is ratified, not assumed.
**Evidence basis:** Fact (V2's `CLAUDE.md` requires "an offline deterministic mode and
AI-disabled continuity path"; ADR-001's stack introduces networked dependencies; sponsor
decision on EAB-2).

## Context

V2 was genuinely offline-capable: a static app with zero network dependency. V3's directed
stack (ADR-001) includes an LLM provider, LangSmith, and Redis — two of them networked
services. This is EAB-2 from `docs/product/discovery/evidence_acquisition_backlog.md`, and
it is a real departure from a stated V2 non-negotiable, not a detail.

## Decision

V3 targets **degraded-mode-safe**, defined as: every hosted dependency has an explicit,
documented fallback that preserves *correctness* even when it sacrifices *capability*.
Specifically (from `docs/architecture/c4/boundary_and_degraded_mode.md`):

| Dependency | Fallback |
|---|---|
| LLM provider unreachable | Rules-only deterministic mode for non-generative steps; **abstain** on anything requiring generation — never guess |
| LangSmith unreachable | Trace locally to the owned audit store, sync later; never block the request (ADR-006) |
| Redis unreachable | No-cache mode; **never** serve a stale response as-if-cached |
| MCP tool server unreachable | Agent abstains and escalates to HITL; never proceeds on unretrieved evidence |
| Policy Engine unreachable | **Fail closed** — refuse the request (ADR-005) |

V2's "AI-disabled continuity path" requirement is satisfied by the LLM-unreachable row: the
deterministic rules layer (evidence-authority gating per ADR-003, unit/identity checks) runs
without any model call.

## Alternatives considered

- **Preserve literal offline capability** — rejected: incompatible with a LangGraph/LLM
  architecture. Claiming it would be false.
- **Ignore the tension** — rejected: it would silently drop a stated non-negotiable.

## Drivers

Honesty about a real constraint change; preserving the *intent* behind V2's rule (the system
must not become unusable or unsafe when a dependency fails).

## Consequences

- **Easier:** each dependency's failure behavior is explicit and testable rather than
  assumed.
- **Harder:** every fallback path needs its own test coverage (Stage 14).
- **Riskier:** V3 genuinely cannot run air-gapped. If the sponsor requires true air-gap, the
  entire stack decision (ADR-001) reopens.

## Guardrails

No fallback may trade correctness for availability. "Fail closed" for authorization,
"degrade gracefully" for observability — never the reverse.

## Validation

Stage 14: run the eval suite with each dependency disabled in turn; all correctness gates
must still pass (capability may reduce).

## Known limitation (recorded, not papered over)

This decision is correct for the capstone/workshop deployment context. **A real deployment
inside a GxP manufacturing network would likely require the air-gapped variant** — self-hosted
open-weight models on on-prem GPUs and a self-hosted trace backend — which would change model
choice, cost model, eval approach, and probably output quality. That variant is out of scope
here by explicit sponsor decision, and is recorded so the limitation is visible to anyone
reading this as a production design rather than discovered later.

## Revisit triggers

If the deployment target changes to a GxP manufacturing network or any environment without
outbound internet, this ADR and ADR-001 both reopen. The V2 non-negotiable that motivated
the original tension ("AI-disabled continuity path") remains satisfied either way by the
deterministic rules layer.

## Addendum — regional platform outage (Stage 21 gap-closure, INJ-079)

"The primary AI region fails during batch review and expedited safety reporting" is not a
new failure mode this ADR needs a new row for — it is the **LLM provider unreachable** row
above, under a specific cause. The graph does not distinguish *why* the provider is
unreachable (region failure, rate limiting, network partition, provider outage); every one
of those causes hits the same `except Exception` boundary in `synthesize`/`critic_verify`
(`services/api/graph.py`, `pv_graph.py`, `supply_graph.py`) and produces the same
`degraded_mode` abstention, tested by `eval-ai-cache/eval_dataset/12_model_substitution_regression.json`'s
MSR-02. There is no separate multi-region failover in this build — deliberately: building
one would mean silently retrying into a second region on a caller's behalf, which is a
retry-on-failure behavior this system's own no-guess principle (ADR-007's core rule) argues
against for anything touching generation. A region failure during expedited safety
reporting means that run **abstains**, not that it silently reroutes and reports as if
nothing happened; a human is what handles the case in the meantime, the same as any other
`degraded_mode` abstention.

## Addendum — OT segmentation and ransomware isolation (Stage 21 gap-closure, INJ-069)

AEGIS reads Manufacturing evidence (MES, historians, eBR) only through the
`evidence.retrieve` tool, over a network boundary it does not control the availability
of — it never holds a direct OT-network connection (`docs/architecture/c4/c4_context.md`
already scopes Manufacturing as a read-only external evidence source, not a system AEGIS
is inside of). This means the specific scenario INJ-069 describes — Manufacturing
historians isolated for ransomware containment while MES/QMS run in degraded mode — is
**already covered by this ADR's existing dependency-outage row**, not a new failure mode:
an isolated OT network is indistinguishable, from AEGIS's side of the boundary, from any
other `evidence.retrieve` outage. The graph's real behavior is unchanged and already
tested: `STORE_UNAVAILABLE` from the retrieval tool → the run abstains with
`dependency_unavailable`, never guesses at what an isolated system would have said.

What this addendum closes is the *belief* that OT segmentation was an unaddressed gap; it
was already handled by construction, because AEGIS was never designed to be inside the OT
trust boundary in the first place. It does not, and cannot, say anything about OT network
segmentation itself — that is Manufacturing's own infrastructure control, entirely outside
this application's boundary, and no code in this repository could honestly claim to
enforce it.
