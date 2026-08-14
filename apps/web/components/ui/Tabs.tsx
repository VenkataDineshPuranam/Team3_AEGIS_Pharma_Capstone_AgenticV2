"use client";

import { useRef, type ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * Tabs, with the full WAI-ARIA keyboard contract: arrow keys move between tabs, Home/End
 * jump to the ends, and only the active tab is in the page's tab order (roving tabindex),
 * so Tab moves out of the tablist rather than through every tab in it.
 */
export function Tabs<T extends string>({
  label,
  value,
  onChange,
  tabs,
  children,
}: {
  label: string;
  value: T;
  onChange: (v: T) => void;
  tabs: { value: T; label: string; count?: number; badge?: ReactNode }[];
  children: ReactNode;
}) {
  const listRef = useRef<HTMLDivElement>(null);

  function onKeyDown(e: React.KeyboardEvent) {
    const index = tabs.findIndex((t) => t.value === value);
    let next = -1;
    if (e.key === "ArrowRight") next = (index + 1) % tabs.length;
    else if (e.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
    else if (e.key === "Home") next = 0;
    else if (e.key === "End") next = tabs.length - 1;
    if (next < 0) return;

    e.preventDefault();
    onChange(tabs[next].value);
    // Move real focus too -- an arrow key that changes the panel but leaves focus behind
    // desynchronizes what a screen reader announces from what is displayed.
    listRef.current?.querySelectorAll<HTMLElement>('[role="tab"]')[next]?.focus();
  }

  return (
    <>
      <div
        ref={listRef}
        role="tablist"
        aria-label={label}
        onKeyDown={onKeyDown}
        className="flex gap-1 overflow-x-auto border-b border-[var(--border-subtle)]"
      >
        {tabs.map((tab) => {
          const active = tab.value === value;
          return (
            <button
              key={tab.value}
              role="tab"
              id={`tab-${tab.value}`}
              aria-selected={active}
              aria-controls={`panel-${tab.value}`}
              tabIndex={active ? 0 : -1}
              onClick={() => onChange(tab.value)}
              className={cn(
                "relative shrink-0 whitespace-nowrap px-3 py-2.5 text-[13px] font-medium transition-colors",
                active
                  ? "text-[var(--text-primary)]"
                  : "text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]",
              )}
            >
              <span className="inline-flex items-center gap-1.5">
                {tab.label}
                {tab.count != null && (
                  <span
                    className={cn(
                      "tnum rounded-[var(--radius-full)] px-1.5 py-0.5 text-[10px]",
                      active
                        ? "bg-[var(--brand-subtle)] text-[var(--brand)]"
                        : "bg-[var(--surface-sunken)] text-[var(--text-tertiary)]",
                    )}
                  >
                    {tab.count}
                  </span>
                )}
                {tab.badge}
              </span>
              {active && (
                <span
                  aria-hidden="true"
                  className="absolute inset-x-0 -bottom-px h-0.5 bg-[var(--brand)]"
                />
              )}
            </button>
          );
        })}
      </div>
      <div
        role="tabpanel"
        id={`panel-${value}`}
        aria-labelledby={`tab-${value}`}
        tabIndex={0}
        className="pt-4 focus-visible:outline-none"
      >
        {children}
      </div>
    </>
  );
}
