# web

Operator / approver workbench for the AEGIS Pharma AI system — governed case files for
`batch_review`, `pv_intake`, and `supply_planning`. Decision support only: approve means
accept the evidence pack, never certify / allocate / determine safety.

Next.js 16 (App Router, TypeScript), Tailwind. Requires the Orchestrator API
(`uvicorn services.api.main:app --port 8000` from the repo root).

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Ops console is a separate app at
[http://localhost:3001](http://localhost:3001).

## Pages

- `/` — role home (pending, clocks at risk)
- `/inbox` — HITL queue with SLA chrome
- `/inbox/[runId]` — case file (findings, evidence drawer, justification, dual-leg / veto)
- `/workflows/*` — per-workflow workspaces
- `/runs` — history including timed-out (T3: "No decision was made; resubmit.")

## Stated gaps

- Role switcher is an Entra ID stub, not real SSO (ADR-009).
- HITL ladder is shown in the UI; graph-side wall-clock enforcement is still P-08.
