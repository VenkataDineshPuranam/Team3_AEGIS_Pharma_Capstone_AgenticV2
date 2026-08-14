"use client";

import { cn } from "@/lib/cn";
import { Badge, type BadgeTone } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/States";
import type { AuditEvent } from "@/lib/api";
import { formatDateTime, humanize } from "@/lib/format";

/**
 * Audit timeline.
 *
 * Real events only. This renders exactly what the audit store holds for a run and nothing
 * else — no interpolated "evidence retrieved" or "guard evaluated" steps to make the
 * sequence look fuller. Those node-level events are traced to LangSmith, not written to
 * this store, and the footnote says so rather than leaving the gap to be misread as
 * "nothing happened between these two timestamps".
 */

const EVENT_META: Record<
  string,
  { label: string; tone: BadgeTone; description: string }
> = {
  AgentRun: {
    label: "Run finalized",
    tone: "info",
    description:
      "The mandatory audit write. No response can reach a caller without this record existing.",
  },
  HumanOverrideRecorded: {
    label: "Human decision",
    tone: "ok",
    description: "An accountable human recorded a decision, with justification.",
  },
  HitlEscalation: {
    label: "Escalation evaluated",
    tone: "pending",
    description: "The escalation ladder widened the set of eligible approvers.",
  },
  HitlExpired: {
    label: "Approval window expired",
    tone: "abstained",
    description: "No action was taken. A timeout is never an implicit approval.",
  },
  ProhibitedActionBlocked: {
    label: "Prohibited action blocked",
    tone: "blocked",
    description: "The runtime guard matched a prohibited term and stopped the output.",
  },
};

export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  if (events.length === 0) {
    return (
      <EmptyState
        title="No audit records for this run"
        description="Nothing has been written to the append-only audit store under this run id. A run writes its record when it finalizes, so a run still paused for approval has no entry here yet."
      />
    );
  }

  return (
    <div>
      <ol className="relative space-y-0">
        {events.map((event, index) => {
          const meta = EVENT_META[event.event_type] ?? {
            label: humanize(event.event_type),
            tone: "neutral" as BadgeTone,
            description: "",
          };
          const last = index === events.length - 1;

          return (
            <li key={`${event.at}-${index}`} className="relative flex gap-3 pb-5 last:pb-0">
              {/* rail */}
              <div className="flex flex-col items-center">
                <span
                  aria-hidden="true"
                  className={cn(
                    "mt-1 size-2.5 shrink-0 rounded-full ring-4 ring-[var(--surface-raised)]",
                    {
                      ok: "bg-[var(--status-ok-fg)]",
                      info: "bg-[var(--status-info-fg)]",
                      pending: "bg-[var(--status-pending-fg)]",
                      blocked: "bg-[var(--status-blocked-fg)]",
                      abstained: "bg-[var(--status-abstained-fg)]",
                    }[meta.tone as string] ?? "bg-[var(--text-tertiary)]",
                  )}
                />
                {!last && (
                  <span
                    aria-hidden="true"
                    className="mt-1 w-px flex-1 bg-[var(--border-default)]"
                  />
                )}
              </div>

              {/* body */}
              <div className="min-w-0 flex-1 pb-1">
                <div className="flex flex-wrap items-center gap-2">
                  <time
                    dateTime={event.at}
                    className="tnum font-mono text-[12px] text-[var(--text-tertiary)]"
                  >
                    {formatDateTime(event.at)}
                  </time>
                  <Badge tone={meta.tone} size="xs">
                    {meta.label}
                  </Badge>
                </div>

                <p className="mt-1 text-[13px] font-medium text-[var(--text-primary)]">
                  {event.action}
                </p>

                {(event.actor || event.role) && (
                  <p className="mt-0.5 text-[12px] text-[var(--text-secondary)]">
                    {event.role ? (
                      <>
                        <span className="text-[var(--text-tertiary)]">Role:</span> {event.role}
                      </>
                    ) : (
                      <>
                        <span className="text-[var(--text-tertiary)]">Actor:</span> {event.actor}
                      </>
                    )}
                  </p>
                )}

                <EventMetadata metadata={event.metadata} />
              </div>
            </li>
          );
        })}
      </ol>

      <p className="mt-4 border-t border-[var(--border-subtle)] pt-3 text-[11px] leading-relaxed text-[var(--text-tertiary)]">
        This is the complete contents of the append-only audit store for this run. Node-level
        execution events — evidence retrieval, guard evaluations, Critic verification — are
        emitted as LangSmith traces rather than audit records, so they do not appear here.
        Nothing has been reconstructed or inferred to fill the gap.
      </p>
    </div>
  );
}

/**
 * Metadata, rendered as labelled fields rather than a JSON blob (Phase 8).
 *
 * `justification` is pulled out and given its own treatment: it is the human's own words,
 * and burying the most accountability-bearing field in this product inside a metadata
 * list would be exactly the wrong emphasis.
 */
function EventMetadata({ metadata }: { metadata: Record<string, unknown> }) {
  const entries = Object.entries(metadata).filter(
    ([, value]) => value !== null && value !== undefined && value !== "",
  );
  if (entries.length === 0) return null;

  const justification = metadata.justification as string | undefined;
  const rest = entries.filter(([key]) => key !== "justification");

  return (
    <>
      {justification && (
        <blockquote className="mt-2 border-l-2 border-[var(--border-strong)] bg-[var(--surface-sunken)] py-1.5 pl-3 pr-2">
          <p className="text-[10px] uppercase tracking-wider text-[var(--text-tertiary)]">
            Justification recorded
          </p>
          {/* Rendered as text, never as HTML. */}
          <p className="mt-1 text-[13px] leading-relaxed text-[var(--text-primary)]">
            {justification}
          </p>
        </blockquote>
      )}

      {rest.length > 0 && (
        <dl className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
          {rest.map(([key, value]) => (
            <div key={key} className="flex items-baseline gap-1.5">
              <dt className="text-[11px] text-[var(--text-tertiary)]">{humanize(key)}:</dt>
              <dd className="text-[11px] text-[var(--text-secondary)]">{renderValue(value)}</dd>
            </div>
          ))}
        </dl>
      )}
    </>
  );
}

function renderValue(value: unknown): string {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object" && value !== null) {
    return Object.entries(value)
      .map(([k, v]) => `${humanize(k)}: ${v}`)
      .join("; ");
  }
  return String(value);
}
