# web

Approver Dashboard for the AEGIS Pharma AI agentic system -- the human-in-the-loop
interface for `batch_review`, `pv_intake`, and `supply_planning` (Stage 20a/20b,
`services/api/graph.py` / `pv_graph.py` / `supply_graph.py`). Talks to the Orchestrator
API (`services/api/main.py`, FastAPI) over HTTP; no direct access to the LangGraph engine,
Neo4j, or Redis from this app.

Next.js 16 (App Router, TypeScript), Tailwind CSS. No charting library -- observability
panels render as stat cards/tables from real `packages/observability/dashboard_data.py`
numbers, not synthetic data.

## Pages

- `/` -- Approver Dashboard. Polls the pending-decision queue every 4s, review a draft +
  citations, approve/reject/veto (PV) or dual-leg approve/reject (Supply Planning).
- `/submit` -- submit a new run against one of the synthetic fixtures
  (`tests/fixtures/synthetic/`) to see it appear in the queue.
- `/observability` -- real cost/guardrail-trip/cache/terminal-state numbers, per workflow.

## Run

Requires the Orchestrator API running first (`uvicorn services.api.main:app --port 8000`
from the repo root -- see `services/api/main.py`), which itself requires the same
`.env` as the rest of the repo (Neo4j, Redis, `LLM_PROVIDER`).

```bash
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL, no secrets
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Known simplifications (stated, not hidden)

- No auth/login -- requester role is a free-text field, not Entra ID (ADR-009's real
  auth target). Fine for a demo, not for anything real.
- The pending-approval queue (`services/api/pending_queue.py`) is in-memory, single
  process -- doesn't survive an API restart. The audit trail
  (`services/integration/audit_store.py`) is unaffected and remains the real record.
