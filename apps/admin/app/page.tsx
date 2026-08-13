"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/AdminShell";
import { StatCard } from "@/components/StatCard";
import { getHealth, type HealthResponse } from "@/lib/api";

export default function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((e) => setError(e instanceof Error ? e.message : "Unknown error"));
  }, []);
  return (
    <AdminShell title="System health">
      {error && <p className="text-sm text-crimson">{error}</p>}
      {health && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {Object.entries(health.dependencies).map(([name, d]) => (
            <StatCard
              key={name}
              label={name}
              value={d.ok ? "ok" : d.mode ?? "down"}
              tone={d.ok ? "good" : name === "policy_engine" || name === "checkpointer" ? "danger" : "warn"}
            />
          ))}
        </div>
      )}
      <p className="mt-4 text-xs text-muted">
        Policy engine or checkpointer down refuses new runs (fail closed). LangSmith down does not block
        operators. Redis down is no-cache, never a stale serve.
      </p>
    </AdminShell>
  );
}
