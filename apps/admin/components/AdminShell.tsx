"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getHealth, type HealthResponse } from "@/lib/api";

const NAV = [
  { href: "/", label: "Health" },
  { href: "/runs", label: "Run inspector" },
  { href: "/guardrails", label: "Guardrails" },
  { href: "/observability", label: "Observability" },
  { href: "/governance", label: "Governance" },
];

function Banner() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() =>
        setHealth({
          status: "down",
          workflows: [],
          dependencies: { orchestrator: { ok: false, detail: "API unreachable", mode: "fail_closed" } },
        }),
      );
  }, []);
  const down = Object.entries(health?.dependencies ?? {}).filter(([, v]) => !v.ok);
  if (!down.length) return null;
  return (
    <div className="border-b border-crimson/30 bg-crimson/10 px-4 py-2 text-sm text-crimson">
      Degraded: {down.map(([n, v]) => `${n} (${v.mode})`).join("; ")}
    </div>
  );
}

export function AdminShell({ title, children }: { title: string; children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="flex min-h-full">
      <aside className="flex w-60 shrink-0 flex-col bg-navy text-white">
        <div className="border-b border-white/10 px-4 py-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-white/50">NovaCura</div>
          <div className="mt-1 font-semibold">AEGIS Ops</div>
          <p className="mt-1 text-xs text-white/60">Audit store is source of truth</p>
        </div>
        <nav className="flex-1 space-y-0.5 p-3 text-sm">
          {NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded px-3 py-2 ${active ? "bg-white/15" : "text-white/75 hover:bg-white/10"}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <a className="border-t border-white/10 p-3 text-xs text-white/50 hover:text-white" href="http://localhost:3000">
          ← Workbench
        </a>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <Banner />
        <header className="border-b border-line bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-navy">{title}</h1>
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
