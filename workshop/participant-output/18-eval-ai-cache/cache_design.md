# Cache Design — Stage 14

**Executes:** `prompts/18_eval_ai_cache.md` §3
**Builds on:** `../../../docs/quality/dmaic-lean/waste_register_downtime.md` (D5, I1),
`tool_inventory.md` §6 (Stage 11's cacheability findings),
`../../../docs/architecture/ontology/conflict_authority_rules.md`
**Artifact status:** `stable` (design); **not built** — cache is excluded from the interim
slice (20a) entirely, per `interim_state.md` and the ADR-003 guardrail

---

## 0. This design is not implemented at 20a, on purpose

Repeating this loudly because it is easy to lose track of across 14 stages: **the interim
state deliberately excludes the cache.** `docs/product/state/interim/interim_state.md` §2:
*"Redis cache — No — deliberately excluded... Caching adds the stale-authority correctness risk
on top of the agent-correctness risk. Introducing both at once makes failures ambiguous."*
Nothing in this document changes that. This is the design Stage 15 implements, once the
uncached path has been proven correct at 20a.

## 1. Two-tier strategy: exact-match, then semantic

| Tier | What it catches | Applies to |
|---|---|---|
| **Exact-match** | Identical query + identical evidence/inventory snapshot | All cacheable tools (§3) |
| **Semantic (embedding similarity)** | Near-duplicate queries against an unchanged snapshot (e.g. two phrasings of the same evidence question) | `evidence.retrieve`, `batch.reconcile` only — never the two do-not-cache tools |

**Semantic matching is deferred to Stage 15 for a specific reason, not laziness.** An embedding
model choice and similarity threshold are exactly the kind of number this programme refuses to
set without measurement (`build_constraints_from_lean.md` BC-13/14 pattern, applied here to
cache tuning). Setting a threshold now would be guessing at false-positive risk with no data.
**What this stage fixes instead:** the semantic tier, whenever it's built, inherits every
exact-match correctness rule below unchanged — a semantic hit is still subject to the same
snapshot-version and citability checks as an exact-match hit. The embedding model and threshold
are the only things Stage 15 gets to choose freely.

## 2. Cache key derivation — the ADR-003 guardrail, made concrete

**Source of truth, not re-derived:** `tool_inventory.md` §6 already stated the rule for
`evidence.retrieve`: *"Cache key must be `hash(query, evidence_snapshot_version)`"* — because a
key built only from the query text cannot distinguish a hit taken before a supersession from
one taken after (register row D5). This document extends that rule to every cacheable tool:

| Tool | Cache key |
|---|---|
| `evidence.retrieve` (any scope) | `hash(query.terms, evidence_snapshot_version)` — **not** `policy_contract_version`; retrieved content doesn't change with policy, only request admission does (a distinction verified, not assumed — see `tool_inventory.md` §5 vs §6) |
| `batch.reconcile` | `hash(evidence_ids[], policy_contract_version)` — identical to its idempotency key (`batch_reconcile.schema.json`), since the tool's output is deterministic given the same evidence set and policy |
| `pv.normalize_terminology` | `hash(source_text, terminology_table_version)` |

**Verified this stage, not assumed:** `graders/cache_correctness_grader.py:grade_cache_key_includes_snapshot`
is an executable check that a proposed cache key includes the snapshot field — it fails any key
missing it. This runs in `cache_correctness_evals.md`.

## 3. The do-not-cache list — enforced in code, not just documented

**Exit criterion:** "Cache do-not-cache list is enforced in code, not just documented." Two
tools, both already identified at Stage 11 (`tool_inventory.md` §6), now backed by an
executable check:

| Tool | Why | Enforcement |
|---|---|---|
| `pv.duplicate_check` | A case not a duplicate at time T can become one as new cases arrive — caching risks silently serving a stale duplicate verdict | `graders/cache_correctness_grader.py:grade_no_cache_list_enforced` fails any cache-write attempt for this tool |
| `supply.generate_options` | Depends on the most volatile data in the system (inventory, quality status); a cached option set can recommend against inventory that no longer exists | Same grader, same enforcement |

**Anything touching a prohibited-decision path is also never cached** — this has no separate
enforcement mechanism because it needs none: the Prohibited-Action Guard runs on every response
regardless of whether it came from cache or a fresh call (`langgraph_design.md`'s guard nodes
sit downstream of both paths in the graph, not just the fresh-generation path). A cached
response is not exempt from the guard.

## 4. TTL per workflow risk tier

| Tier | Tools | TTL | Basis |
|---|---|---|---|
| **Low volatility** | `pv.normalize_terminology` (pure function of a versioned table) | Until `terminology_table_version` changes | No time-based expiry needed — version-keyed already invalidates correctly |
| **Medium volatility** | `evidence.retrieve`, `batch.reconcile` | **Until the next `EvidenceConflictDetected` or supersession event for any cited `evidence_id`**, not a fixed duration | A time-based TTL would either be too short (wasting the cache) or too long (risking a stale serve) without knowing supersession frequency — event-driven invalidation is correct regardless of that unknown number |
| **Never cached** | `pv.duplicate_check`, `supply.generate_options` | N/A | §3 |

**No tool in this design uses a plain wall-clock TTL as its primary invalidation mechanism.**
Every cacheable tool is invalidated by a **version or event change**, because a wall-clock TTL
can't distinguish "still correct" from "coincidentally not yet expired" — the two failure modes
this whole document exists to prevent.

## 5. Invalidation trigger — one mechanism, not per-tool logic

A single event, `EvidenceSnapshotAdvanced` (fired whenever `knowledge_catalog.csv`'s ingested
state changes — a new document, a status transition, a new `supersedes` edge), invalidates
every cache entry keyed on the prior `evidence_snapshot_version`. This is simpler and safer
than per-tool invalidation logic: **the cache never needs to know *why* a snapshot changed**,
only that it did — consistent with `conflict_authority_rules.md` §3's rule that supersession is
normalized once, centrally, never re-derived downstream.

## 6. What this design explicitly does not do

| Not done | Why | Where it belongs |
|---|---|---|
| Set a similarity threshold for semantic matching | Would be guessing (BC-13/14 pattern) | Stage 15, from measured false-positive data |
| Choose an embedding model | Same reason | Stage 15 |
| Set a numeric hit-rate target | Baseline is N/A — no cache exists to measure (`dmaic_plan.md` Measure table, U4) | Stage 15 |
| Cache anything from `pv.duplicate_check` or `supply.generate_options` under any condition | §3 | Never — this is a standing rule, not deferred |
