"use client";

import { useEffect, useState } from "react";
import { getHealth, type HealthResponse } from "@/lib/api";

export function DegradedBanner() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = () =>
      getHealth()
        .then((h) => !cancelled && setHealth(h))
        .catch(() => {
          if (!cancelled) {
            setHealth({
              status: "down",
              workflows: [],
              dependencies: {
                orchestrator: { ok: false, detail: "API unreachable", mode: "fail_closed" },
              },
            });
          }
        });
    load();
    const id = setInterval(load, 15000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (!health) return null;
  const down = Object.entries(health.dependencies).filter(([, v]) => !v.ok);
  if (down.length === 0) return null;

  return (
    <div className="border-b border-crimson/30 bg-crimson/10 px-4 py-2 text-sm text-crimson" role="status">
      <strong className="font-semibold">Degraded mode.</strong> Capability reduced; correctness preserved.
      <ul className="mt-1 space-y-0.5">
        {down.map(([name, v]) => (
          <li key={name}>
            {name}: {v.mode ?? "unavailable"} — {v.detail}
          </li>
        ))}
      </ul>
    </div>
  );
}
