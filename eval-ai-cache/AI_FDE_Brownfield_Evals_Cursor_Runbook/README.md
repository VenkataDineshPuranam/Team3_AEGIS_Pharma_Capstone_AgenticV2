# AI FDE Brownfield Evals — Cursor Runbook

**Mode:** Cursor AI only  
**MCP:** Not used  
**Target:** Existing brownfield repository  
**Goal:** Discover → Baseline → Evaluate → Gate → RCA → Fix → Regression → Re-run → Integrity Audit → Final Report

## Execution order

Run the Markdown prompt files in numeric order:

1. `00_Cursor_Eval_Rule.md`
2. `01_Repo_Reconnaissance.md`
3. `02_Evalability_Gap_Analysis.md`
4. `03_Historical_Bug_Regression_Mining.md`
5. `04_Design_Eval_Harness.md`
6. `05_Build_Harness_and_Self_Test.md`
7. `06_Build_Eval_Dataset.md`
8. `07_Correctness_Evals.md`
9. `08_Grounding_and_Authority_Evals.md`
10. `09_Safety_and_Security_Evals.md`
11. `10_Trajectory_and_Human_Oversight.md`
12. `11_Reliability_Evals.md`
13. `12_Performance_and_Cost_Evals.md`
14. `13_Business_Outcome_Evals.md`
15. `14_Define_Eval_Gates.md`
16. `15_Baseline_Eval_Run.md`
17. `16_Root_Cause_Analysis.md`
18. `17_Fix_Confirmed_Defects.md`
19. `18_Fix_Eval_Harness_Defects.md`
20. `19_Repeatability_and_Flakiness.md`
21. `20_Complete_Regression_Run.md`
22. `21_Eval_Integrity_Audit.md`
23. `22_Final_Eval_Run.md`
24. `23_Final_AI_FDE_Evaluation_Report.md`

## Workshop operating rules

- Run prompts sequentially.
- Prefer a fresh Cursor chat for major phases if context becomes noisy.
- Do not skip the baseline run.
- Do not fix defects before RCA.
- Do not weaken evals to manufacture PASS results.
- Every confirmed application defect that is fixed must become a regression case.
- Preserve `NOT_OBSERVABLE`, `NOT_APPLICABLE`, and `THRESHOLD_NOT_DEFINED` honestly.
- Hard-gate failures must not be averaged away.
- Reuse the repository's existing language, test framework, fixtures, mocks, and CI conventions.
- No MCP, no mandatory external eval SaaS, no mandatory external telemetry collector.
