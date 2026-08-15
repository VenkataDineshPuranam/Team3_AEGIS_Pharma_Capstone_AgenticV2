# Evidence Acquisition Backlog — Stage 01 (Discovery)

Required because two AI FDE inputs (User workflow, Constraints) scored `Partial` in
`discovery.md` §10. Framing mode remains `decision-ready` overall (see §10
rationale), but these items should be closed before the stages they block.

| ID | Item | Likely owner/source | Why it blocks | Blocks (stage) | Priority |
|---|---|---|---|---|---|
| EAB-1 | Confirm whether V2 reuses/extends V1's `ASSESSMENT_RUBRIC.csv` / `SCORING_MODEL.md` or needs its own rubric | User/sponsor | Without this, Stage 21's final-defense pack doesn't know what it's being scored against | 21 | Blocks production |
| ~~EAB-2~~ | ~~Resolve offline-compatibility vs. hosted-LangSmith tension~~ | — | **CLOSED** — sponsor confirmed cloud-connected operation is acceptable; ADR-007 ratified, air-gapped production variant recorded as a known limitation | — | **Closed** |
| ~~EAB-3~~ | ~~Determine if a V2-specific case/stakeholder-pack addendum is needed~~ | — | **CLOSED** — no addendum needed; V1's `case/STAKEHOLDER_PACK.md` already defines 15 roles with explicit decision authority, three of which map exactly onto the workflows. See [`hitl_control_model.md`](../../governance/hitl_control_model.md) | — | **Closed** |
| EAB-4 | Confirm V2's audience: same FDE workshop participants as V1, or a different audience | User | Changes formality/tone of Stage 21 documentation and whether a workshop rubric applies at all | 21 | Blocks framing |
| EAB-5 | Re-verify prior-exploration derivations (inject count = 84, dimension count = 13) directly against `data/injects.json` | Whoever executes Stage 02 | Low severity — informational correction only, does not block design | 02 | Low |
| EAB-6 | Quantify realistic token/cost budgets per workflow before committing to a specific agent count/topology | Architecture owner (Stage 10/15) | Prevents Stage 04 from committing to an over-built multi-agent topology that Stage 15 later has to walk back | 04, 15 | Blocks design |

None of these items are severe enough to force a `hypothesis` framing mode for Stage 02
(SCQA) — see `discovery.md` §10 for the reasoning. They should be tracked and
closed opportunistically as their blocking stage is reached.
