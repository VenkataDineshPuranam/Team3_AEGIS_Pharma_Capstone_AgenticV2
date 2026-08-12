# Evidence Acquisition Backlog — Stage 01 (Discovery)

Required because two AI FDE inputs (User workflow, Constraints) scored `Partial` in
`discovery.md` §10. Framing mode remains `decision-ready` overall (see §10
rationale), but these items should be closed before the stages they block.

| ID | Item | Likely owner/source | Why it blocks | Blocks (stage) | Priority |
|---|---|---|---|---|---|
| EAB-1 | Confirm whether V3 reuses/extends V2's `ASSESSMENT_RUBRIC.csv` / `SCORING_MODEL.md` or needs its own rubric | User/sponsor | Without this, Stage 21's final-defense pack doesn't know what it's being scored against | 21 | Blocks production |
| EAB-2 | Resolve offline-compatibility vs. hosted-LangSmith tension — does V3 need an air-gapped/local-only mode? | User / architecture decision | Affects whether LangSmith is mandatory or one of two supported observability backends; changes Stage 04's target architecture and Stage 08's ADR-0001 | 04, 08 | Blocks design |
| ~~EAB-3~~ | ~~Determine if a V3-specific case/stakeholder-pack addendum is needed~~ | — | **CLOSED** — no addendum needed; V2's `case/STAKEHOLDER_PACK.md` already defines 15 roles with explicit decision authority, three of which map exactly onto the workflows. See [`hitl_control_model.md`](../../governance/hitl_control_model.md) | — | **Closed** |
| EAB-4 | Confirm V3's audience: same FDE workshop participants as V2, or a different audience | User | Changes formality/tone of Stage 21 documentation and whether a workshop rubric applies at all | 21 | Blocks framing |
| EAB-5 | Re-verify prior-exploration derivations (inject count = 84, dimension count = 13) directly against `data/injects.json` | Whoever executes Stage 02 | Low severity — informational correction only, does not block design | 02 | Low |
| EAB-6 | Quantify realistic token/cost budgets per workflow before committing to a specific agent count/topology | Architecture owner (Stage 10/15) | Prevents Stage 04 from committing to an over-built multi-agent topology that Stage 15 later has to walk back | 04, 15 | Blocks design |

None of these items are severe enough to force a `hypothesis` framing mode for Stage 02
(SCQA) — see `discovery.md` §10 for the reasoning. They should be tracked and
closed opportunistically as their blocking stage is reached.
