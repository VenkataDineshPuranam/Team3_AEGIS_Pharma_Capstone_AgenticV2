# admin

Ops / governance console for AEGIS: system health, run inspector, prohibited-action log
(hashes only — never blocked draft text), observability panels from the owned audit store,
and read-only policy / HITL ladder status.

Next.js 16 on port 3001. Talks to the Orchestrator API (`NEXT_PUBLIC_API_URL`).

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3001](http://localhost:3001).
