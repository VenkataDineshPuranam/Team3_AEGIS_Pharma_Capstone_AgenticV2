"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { DegradedBanner } from "./DegradedBanner";
import { RoleSwitcher } from "./RoleSwitcher";

const NAV = [
  { href: "/", label: "Home" },
  { href: "/inbox", label: "Inbox" },
  { href: "/workflows/batch-review", label: "Batch Review" },
  { href: "/workflows/pv-intake", label: "PV Intake" },
  { href: "/workflows/supply-planning", label: "Supply Planning" },
  { href: "/runs", label: "History" },
];

export function AppShell({
  children,
  title,
  variant = "web",
}: {
  children: React.ReactNode;
  title?: string;
  variant?: "web" | "admin";
}) {
  const pathname = usePathname();
  const adminNav = [
    { href: "/", label: "Health" },
    { href: "/runs", label: "Run inspector" },
    { href: "/guardrails", label: "Guardrails" },
    { href: "/observability", label: "Observability" },
    { href: "/governance", label: "Governance" },
  ];
  const items = variant === "admin" ? adminNav : NAV;

  return (
    <div className="flex min-h-full">
      <aside className="flex w-60 shrink-0 flex-col bg-navy text-white">
        <div className="border-b border-white/10 px-4 py-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-white/50">NovaCura</div>
          <div className="mt-1 font-semibold tracking-tight">
            AEGIS {variant === "admin" ? "Ops" : "Workbench"}
          </div>
          <p className="mt-1 text-xs text-white/60">Decision support only</p>
        </div>
        <nav className="flex-1 space-y-0.5 p-3 text-sm">
          {items.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded px-3 py-2 ${
                  active ? "bg-white/15 text-white" : "text-white/75 hover:bg-white/10"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 p-3">
          {variant === "web" && <RoleSwitcher />}
          {variant === "web" && (
            <a
              className="mt-3 block text-xs text-white/50 hover:text-white"
              href="http://localhost:3001"
            >
              Ops console →
            </a>
          )}
          {variant === "admin" && (
            <a
              className="block text-xs text-white/50 hover:text-white"
              href="http://localhost:3000"
            >
              ← Workbench
            </a>
          )}
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <DegradedBanner />
        <header className="border-b border-line bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-navy">{title}</h1>
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
