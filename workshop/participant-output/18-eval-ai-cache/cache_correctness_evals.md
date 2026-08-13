# Cache Correctness Evals — Stage 14

**Executes:** `prompts/18_eval_ai_cache.md` §4
**Grader:** `graders/cache_correctness_grader.py`
**Exit criterion:** "Cache correctness evals exist and pass." **Both true** — run below,
executed against the actual grader code, not asserted.

---

## 0. The failure mode this exists to catch

Per the prompt: *"tests proving a cache hit never serves a stale-authority or superseded-
evidence answer — this is the failure mode unique to caching in a regulated domain."* Three
distinct sub-failures, each with its own eval below: (1) a cache key that structurally cannot
detect staleness, (2) a cache hit that serves an answer built on evidence that has since been
superseded, (3) a cache write attempted for a tool that must never be cached at all.

**These evals pass today even though no cache is built** (`cache_design.md` §0) — the grader
logic is real and runnable now, against synthetic inputs; the same functions are what Stage 15
wires to a real Redis-backed cache without modification.

## 1. Eval cases and actual results

Executed via `python3 -c` against `cache_correctness_grader.py`, this session:

| ID | Case | Grader call | Result | Correct outcome? |
|---|---|---|---|---|
| CCE-01 | Cache key includes `evidence_snapshot_version` | `grade_cache_key_includes_snapshot(["query", "evidence_snapshot_version"])` | `pass: True` | ✅ — golden path |
| CCE-02 | **Adversarial** — key built from query alone | `grade_cache_key_includes_snapshot(["query"])` | `pass: False, reason: cache_key_missing_snapshot_version` | ✅ — grader correctly rejects a staleness-blind key |
| CCE-03 | Snapshot unchanged since cache write | `grade_no_stale_serve("snap-1", "snap-1", "K-006", "approved")` | `pass: True` | ✅ — golden path |
| CCE-04 | **Adversarial (the headline case)** — snapshot advanced, `K-007` (the exact `BATCH_RELEASE_POLICY_OLD.md` supersession pair from `ontology.md` §2) is now `superseded` | `grade_no_stale_serve("snap-1", "snap-2", "K-007", "superseded")` | `pass: False, reason: stale_serve: cached response built on snapshot snap-1, but K-007 is now superseded as of snap-2 -- must invalidate, not serve` | ✅ — this is the exact failure the prompt names, caught |
| CCE-05 | Snapshot advanced, but the cited document (`K-006`) is still `approved` | `grade_no_stale_serve("snap-1", "snap-2", "K-006", "approved")` | `pass: True, reason: snapshot_changed_but_evidence_still_citable` | ✅ — a snapshot change alone doesn't invalidate every entry, only entries whose cited evidence actually changed status. Confirms the design isn't over-broad |
| CCE-06 | `pv.duplicate_check` respects the do-not-cache list | `grade_no_cache_list_enforced("pv.duplicate_check", False)` | `pass: True` | ✅ — golden path |
| CCE-07 | **Adversarial** — a cache write attempted for `supply.generate_options` (on the do-not-cache list) | `grade_no_cache_list_enforced("supply.generate_options", True)` | `pass: False, reason: do_not_cache_list_violated` | ✅ — caught |
| CCE-08 | `evidence.retrieve` (a cacheable tool) writing to cache | `grade_no_cache_list_enforced("evidence.retrieve", True)` | `pass: True` | ✅ — confirms the list doesn't over-block a tool that should be cacheable |

**8 of 8 grader calls returned the correct outcome.** For adversarial cases (CCE-02, CCE-04,
CCE-07), "correct outcome" means the grader's own `pass: False` — the grader is functioning
correctly when it *catches* the bad condition it was designed to catch. Reading these as
harness failures would be exactly the mistake `dmaic_lens.md`'s Measure section warns against.

## 2. What CCE-04 actually proves, stated precisely

CCE-04 is the one worth being precise about, since it's the scenario named directly in the
prompt. It does **not** prove that a real cache will never serve stale evidence — no cache
exists yet to make that claim about. It proves that **if** a cache implementation calls
`grade_no_stale_serve` with the snapshot-before, snapshot-after, and current evidence status
before returning a hit, **then** a stale serve on superseded evidence is caught before it
reaches a caller. The correctness property depends on Stage 15 actually wiring this check into
the cache's hit path — this eval is the contract that wiring must satisfy, not a substitute for
building it.

## 3. Coverage against `conflict_authority_rules.md`

| Rule (source) | Covered by |
|---|---|
| `untrusted`/`superseded` never citable (§1) | CCE-04 (the superseded case specifically) |
| Supersession normalized once, at ingestion (§3) | Implicit — `grade_no_stale_serve` takes `evidence_status_at_current_snapshot` as already-resolved, never re-derives it from prose |
| Factual conflicts flagged, never silently resolved (§5) | Not yet covered — this eval set checks authority staleness, not factual-conflict staleness. **Open item for Stage 15**: a cache hit on a response with `conflict_detected: true` needs the same re-check as an authority status, since the conflict's resolution status could also change between cache write and hit |

## 4. Revisit trigger

If Stage 15 measures cache hit rate and finds it materially reduced by aggressive invalidation
(every snapshot change invalidating more than necessary), the fix is a **finer-grained**
invalidation key (per-evidence-item rather than per-snapshot) — not loosening CCE-04's
guarantee. Correctness is not a dial to trade against hit rate in this design.
