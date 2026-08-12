# ADR Candidates — Stage 03 (C4)

Architecture choices surfaced during C4 that need a decision record at Stage 04. Options
are listed; nothing here is decided yet.

| # | Candidate | Options | Notes |
|---|---|---|---|
| 1 | Runtime stack | LangGraph + LangSmith + Redis (already directed by the user) vs. alternatives | Low-controversy — user has already decided this; still needs a formal ADR-0001 for the record, per `SPEC_DRIVEN_DEVELOPMENT.md` §0 |
| 2 | V3 build strategy: fully separate vs. extend V2's `submission/` | **Decided this session: fully separate** (user's explicit answer) | Should be formalized as an ADR even though already decided, since it materially shapes every later container/service decision — record the trade-offs discussed (duplicated peripheral effort vs. avoiding legacy-stack coupling) |
| 3 | Governance/Policy Engine: separate container vs. embedded in Orchestrator API | Separate (favors independent versioning, matches DDD's open-host-service pattern) vs. embedded (simpler ops, fewer hops) | `c4_containers.md` leans separate but flags this as undecided |
| 4 | Audit/Evidence Log Store: separate from LangSmith vs. LangSmith-only | Separate (compliance retention independent of a third-party SLA) vs. LangSmith-only (less infra) | `c4_containers.md` leans separate |
| 5 | LangGraph deployment topology | One deployment hosting all three workflows' agents vs. three separate deployments | Raised in `context_map.md` as unresolved; affects blast radius and independent scaling |
| 6 | MCP tool authentication/authorization | mTLS, signed tokens, or platform-native auth | Not yet analyzed — needs Stage 11 input too |
| 7 | Redis cache topology | Single shared cluster vs. per-workflow instances; semantic-cache embedding model choice | Feeds Stage 15 |
| 8 | **Verify DDD's rules-vs-AI boundary against V2's actual grader code** | Read `submission/evaluation/graders/temporal_unit_grader.py` and `authority_grader.py` (33 lines each — small, confirmed this session) before Stage 20 locks the schema, to confirm `domain_model.md` §8's assumption about which PV/authority logic is rule-based vs. AI-assisted actually matches what V2's evaluation expects | Raised directly in response to the user's "what do we miss by starting from scratch" question — flagged as a concrete pre-Stage-20 action, not just a documented risk |
| 9 | Degraded-mode/offline-compatibility framing | V3 is "degraded-mode-safe" (every hosted dependency has a defined fallback) rather than V2's "offline-compatible" (zero network dependency) | `boundary_and_degraded_mode.md` proposes this resolution to EAB-2; should be ratified as an ADR since it's a real departure from a V2 non-negotiable, not a minor detail |
