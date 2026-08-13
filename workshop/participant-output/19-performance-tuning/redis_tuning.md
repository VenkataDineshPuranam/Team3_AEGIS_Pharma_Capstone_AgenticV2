# Redis Tuning — Stage 15

**Executes:** `prompts/19_performance_tuning.md` §2
**Consumes:** `../../../eval-ai-cache/1786337982498-Windows Cursor Redis Caching Runbook.docx` (read in
full this stage — NAB-4/trigger T-7, previously unconsumed)
**Builds on:** `../../../eval-ai-cache/cache_design.md` (Stage 14), `../../../docs/quality/dmaic-lean/waste_register_downtime.md` (D5/I1)
**Artifact status:** `stable` (design); **not built** — cache stays excluded from the interim
slice per `interim_state.md`, unchanged from Stage 14

---

## 0. What the consumed runbook actually is, and why that matters

The runbook is a **Cursor-IDE engineering workflow** for adding Redis caching to a brownfield
app — it is not a design document for our system, and reading it surfaced one distinction this
programme had not made explicit before: **it separates an engineering/control plane (a human
developer, via an IDE's MCP connection, inspecting and testing Redis) from the application data
plane (the deployed app's own native Redis client).** Verbatim: *"MCP gives Cursor access to
Redis; it is not the production cache transport... Application runtime uses a native Redis
client."*

**Applied to us:** our LangGraph runtime's Redis cache must use a **native Redis client
library**, never an MCP server, at runtime. This has nothing to do with Stage 11's domain-agent
MCP tool servers (`evidence.retrieve`, etc.) — those are a completely different use of the term
MCP, for a completely different purpose (agent tool calls, not cache inspection). Recorded here
so a future implementer doesn't conflate the two and reach for an MCP-mediated cache path.

## 1. Non-negotiable design rules — consumed verbatim, not re-derived

The runbook's own closing section lists rules that map directly onto decisions this programme
already made independently at Stage 09/14, confirming them rather than introducing anything
new — cited so the convergence is visible, not coincidental-sounding:

| Runbook rule | Already true of our design | Where |
|---|---|---|
| "MCP is not the production cache transport" | New this stage — native client required (§0) | This document |
| "Exact caching is implemented before semantic caching" | Already true — `cache_design.md` §1 defers semantic matching entirely to Stage 15+ measurement | Stage 14 |
| "Security/version context is part of cache identity" | Already true — `hash(query, evidence_snapshot_version)`, not `hash(query)` | Stage 14, ADR-003 guardrail |
| "Side-effecting operations are not semantic-cached" | Already true, and stronger — nothing in our design has a side effect at all (Stage 11: all 7 tools read-only) | Stage 11 |
| "Only validated AI outputs enter the cache" | **A gap this reading found** — see §2 | This document |
| "Redis failure normally causes cache bypass, not application failure" | Already true — ADR-007 degraded-mode-safe | Stage 03/07 |
| "Semantic thresholds are determined by evals, not intuition" | Already true — same BC-13/14 discipline this programme already applies everywhere | Stage 09 |
| "Existing behaviour must remain unchanged when caching is disabled" | Already true by construction — 20a runs with zero cache | Stage 06 |

## 2. Finding: cache placement relative to the guard, not just the tool call

The runbook's flow — *"Model / RAG output → Schema validation → Grounding validation →
Security / guardrail check → Successful response → CACHE"* — makes explicit something
`cache_design.md` (Stage 14) never stated outright: **where in the pipeline caching happens.**
Stage 14 designed cache keys and a do-not-cache list for individual **tool** calls
(`evidence.retrieve`, `batch.reconcile`), which is correct as far as it goes, but never said
whether a cached *tool response* could still be paired with an uncached, un-guarded
*synthesis* — and never said explicitly that nothing produced by `synthesize` should be
cached before it clears `prohibited_action_guard` and the Critic.

**Resolution, extending Stage 14 rather than contradicting it:** two independent cache
placement points, not one:

1. **Tool-response cache** (Stage 14's existing design) — `evidence.retrieve` and
   `batch.reconcile` results, keyed by `evidence_snapshot_version`. Unaffected by this finding.
2. **No synthesis-output cache exists in this design, and none should be added carelessly.**
   If a future stage considers caching `synthesize`'s output directly (to skip re-generation
   for a repeated query against unchanged evidence), it **must** sit downstream of both
   `prohibited_action_guard` passes and the Critic — never cache a draft, only a
   guard-and-Critic-cleared response. This is a build constraint for whichever stage
   eventually proposes synthesis-output caching (not scheduled — no such stage currently
   exists in the execution plan), recorded now so it isn't designed wrong later.

## 3. Two-plane architecture for our system specifically

```
                    ENGINEERING / CONTROL PLANE (human, dev-time only)
                    Claude Code IDE  →  (no MCP-to-Redis path in this repo's design)

┌──────────────────────────── AZURE CACHE FOR REDIS ────────────────────────────┐
│  Tool-response cache (evidence.retrieve, batch.reconcile)                     │
│  keyed: hash(query|evidence_ids, evidence_snapshot_version[, policy_version]) │
└───────────────────────────────▲─────────────────────────────────────────────┘
                                 │
                         Native Redis client
                                 │
                    LANGGRAPH RUNTIME (Orchestrator API, ADR-001/009)
                         retrieve / reconcile tool nodes
```

No MCP anywhere in the application data plane. This matches ADR-009's own guardrail ("no
Azure-specific API may leak into domain or agent logic — platform bindings live in
`packages/config`/`infra/`") extended to Redis: the native client lives in the tool-server
implementation layer (Stage 11's `services/integration/`), not in domain/agent code.

## 4. Eviction policy and memory sizing

**Not covered by the consumed runbook** (it's a single-laptop workshop guide with no
multi-tenant capacity guidance) — stated honestly rather than papered over with an invented
number. What can be set now, and what needs measurement:

| Setting | Value now | Basis |
|---|---|---|
| Eviction policy | `volatile-lru` (evict only keys with a TTL, least-recently-used first) | Every cache entry in this design carries an invalidation mechanism (§Stage 14) or a TTL fallback — no entry should be exempt from eviction, and LRU is the correct default absent measured access-pattern data |
| `maxmemory` | **Not set** | Sizing requires knowing cache entry count and average payload size — both depend on U1-adjacent measurement (retrieval result volume per run), Unknown until 20a |
| Persistence (RDB/AOF) | **Disabled** | This is a correctness-optional performance cache, not a source of truth — per ADR-007, Redis unavailability must degrade to no-cache, so there is nothing here that needs durability across a restart |

## 5. Cluster-failure degraded mode — not silent, per the prompt's own requirement

The prompt explicitly asks for "what happens on cache-cluster failure (degraded mode, not
silent full-price fallback with no alert)." This has two parts, and only one was previously
specified:

- **Correctness on failure: already specified.** ADR-007 + `cache_design.md` §6 — Redis down
  ⇒ bypass to no-cache, never block the request. Unchanged.
- **Alerting on failure: not previously specified anywhere.** This is a genuine gap the prompt
  caught. **Fixed here:** a cache-bypass event must emit `cache.error` / `cache.bypass`
  telemetry (using the exact metric names the consumed runbook's Observability section
  specifies — §6 below), and Stage 17 must wire an alert on a sustained bypass rate, not just
  log it. A silent full-price fallback that nobody notices is exactly the failure mode this
  prompt line names, and prior stages left it implicit.

## 6. Observability metrics — consumed, not re-derived (feeds Stage 17)

The runbook's own metric list, adopted as this system's cache telemetry contract:

```
cache.exact.hit / cache.exact.miss
cache.lookup_ms / cache.write_ms
cache.expired / cache.invalidated
cache.error / cache.bypass
llm.calls_avoided / tokens_avoided / estimated_cost_avoided
```

`tokens_avoided` / `estimated_cost_avoided` connect directly to `token_economics.md` §3 —
once real pricing (already verified, §2 there) meets a real avoided-token count (post-cache,
post-20a), this is where the "value" side of the cache's cost-benefit case gets computed. Not
computed here — no cache exists yet to measure.

**Do not log raw prompts on cache events** — the runbook's own instruction, consistent with
BC-8 (redaction rules before the first trace).

## 7. What this document explicitly defers

| Deferred | Why | To whom |
|---|---|---|
| `maxmemory` value | Needs measured entry volume | Stage 15 measured pass, post-20a |
| Semantic cache similarity threshold | BC-13/14 — needs eval data, not intuition (both this programme's rule and the runbook's own) | Stage 15 measured pass |
| Embedding model choice for semantic cache | Same reasoning | Stage 15 measured pass |
| Cache hit-rate target | No baseline exists (U4) | Stage 15 measured pass |
