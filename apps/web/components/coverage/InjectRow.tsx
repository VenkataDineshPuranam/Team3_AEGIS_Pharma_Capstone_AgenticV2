"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/Badge";
import type { Inject } from "@/lib/api";
import { COVERAGE_STATUS_TONE } from "@/lib/coverage-format";

export function InjectRow({ inject }: { inject: Inject }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <li className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] bg-[var(--surface-raised)]">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        className="flex w-full items-start gap-3 px-3.5 py-2.5 text-left hover:bg-[var(--surface-sunken)]"
      >
        <span className="mt-0.5 shrink-0 font-mono text-[11px] text-[var(--text-tertiary)]">
          {inject.id}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-[13px] font-medium text-[var(--text-primary)]">
            {inject.title}
          </span>
          {!expanded && (
            <span className="mt-0.5 line-clamp-1 block text-[12px] text-[var(--text-tertiary)]">
              {inject.rationale}
            </span>
          )}
        </span>
        <Badge tone={COVERAGE_STATUS_TONE[inject.status]} size="xs" className="mt-0.5 shrink-0">
          {inject.status.replace("_", " ")}
        </Badge>
        <span aria-hidden="true" className="mt-0.5 shrink-0 text-[10px] text-[var(--text-tertiary)]">
          {expanded ? "▲" : "▼"}
        </span>
      </button>

      {expanded && (
        <div className="space-y-2.5 border-t border-[var(--border-subtle)] px-3.5 py-3 pl-[3.75rem]">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
              Scenario
            </p>
            <p className="mt-1 text-[13px] leading-relaxed text-[var(--text-secondary)]">
              {inject.scenario}
            </p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
              V2 coverage assessment
            </p>
            <p className="mt-1 text-[13px] leading-relaxed text-[var(--text-primary)]">
              {inject.rationale}
            </p>
          </div>
          <p className="text-[11px] text-[var(--text-tertiary)]">
            V1 evidence sources referenced by this inject:{" "}
            <span className="font-mono">{inject.v2_evidence_sources}</span>
          </p>
        </div>
      )}
    </li>
  );
}
