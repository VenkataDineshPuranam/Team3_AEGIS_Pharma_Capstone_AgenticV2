"use client";

import { AppShell } from "@/components/AppShell";

export default function ObservabilityRedirect() {
  return (
    <AppShell title="Observability">
      <p className="text-sm text-muted">
        Cost, cache, and guardrail panels live in the ops console so operator review stays on the
        case file.
      </p>
      <a className="mt-3 inline-block text-sm text-batch hover:underline" href="http://localhost:3001/observability">
        Open ops observability →
      </a>
    </AppShell>
  );
}
