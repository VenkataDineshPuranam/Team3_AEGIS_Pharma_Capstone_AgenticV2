# DMAIC Lens — Stage 02 (Frame / SCQA)

**Full cycle**, building on Stage 01's full DMAIC output (`docs/product/discovery/dmaic_lens.md`).

## Define

Restated at Frame level: the Complication describes an **Integration + Token + Defects**
waste risk cluster — integrating a new multi-agent runtime onto an unchanged domain risks
both token overspend (if unbounded) and defect reintroduction (if the prohibited-decision
boundary leaks across an agent handoff). These map directly to Stage 01's AI-specific
register (Token, Integration rows) and DOWNTIME register (Defects row).

## Measure

Success metrics from the Answer that are Measure targets:
- Eval pass rate on V2's 12 categories — baseline **Unknown** (carried from Stage 01,
  unchanged — still not measured).
- Token/cost per workflow run — baseline **Unknown**, target set at Stage 04/15.
- Cache hit rate — **N/A yet** (no cache exists), target set at Stage 15.
- Prohibited-decision violations — target **zero**, measured from Stage 14 onward.

No new baselines were measured at Frame level; this stage inherits Stage 01's Measure gaps
unchanged, which is expected — Frame narrates the decision, it does not run new
measurements.

## Analyze

Do Stage 01's root-cause findings still hold? **Yes, confirmed, with one refinement:** Frame
surfaces a root cause Stage 01 named but did not rank — the *sequencing* itself (domain/
governance before architecture, architecture before app) is the primary lever against nearly
every named risk (Token, Defects, Inventory/cache-staleness). Stage 01 treated sequencing as
one candidate Improve action among several; Frame's SCQA work shows it is actually the
unifying mechanism behind supporting points 1–6 in the Minto pyramid, not just one item on a
list. This is a **correction to relative priority**, not a new finding.

## Improve

The Answer itself is the Improve candidate: additive re-architecture with governance-first
sequencing. It reduces waste (Defects, Token, Inventory risk) without adding new process
waste, because it does not introduce new gates beyond what `SPEC_DRIVEN_DEVELOPMENT.md`
already specifies (one spec-first stage per concern, already planned). **Alternative
rejected:** a "big-bang" simultaneous design of domain + agent topology + governance was
considered implicitly (it's the default failure mode named in point 6) and rejected because
it directly causes the Defects risk (point 2) the Answer is structured to avoid.

## Control

What must be monitored post-decision for this Answer to be judged as working (provisional,
firmed up at Stage 09 consolidation and Stage 12 assurance):
- Each subsequent stage's exit criteria (Stages 03–19) must explicitly confirm it did not
  jump ahead of an unresolved dependency (e.g., Stage 10 must not begin before Stage 06 DDD
  is stable).
- EAB-2 and EAB-6 resolution status should be re-checked at every stage gate through Stage 04
  and Stage 08.

## Waste register updates (carried from Stage 01)

No new waste categories identified at Frame level. One refinement: the **Transportation**
and **Token** entries in Stage 01's registers are now understood to be the two categories
most directly addressed by the Answer's sequencing strategy (rather than independent risks
requiring independent mitigation) — see `waste_register_downtime.md` and
`waste_register_ai_specific.md` in this folder for the carried-forward, annotated registers.
