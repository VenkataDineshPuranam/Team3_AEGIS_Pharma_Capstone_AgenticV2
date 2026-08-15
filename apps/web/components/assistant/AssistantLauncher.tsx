"use client";

import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, SkeletonText } from "@/components/ui/States";
import { useApiResource } from "@/hooks/useApiResource";
import { getQueue, getRunHistory, type QueueEntry, type Workflow } from "@/lib/api";
import { WORKFLOW_LABELS, WORKFLOW_SUBJECT_LABEL } from "@/lib/format";
import { RecordAssistant } from "./RecordAssistant";

/**
 * Global entry point to the Record Assistant.
 *
 * WHY THIS EXISTS ALONGSIDE THE RUN-DETAIL TAB
 * ---------------------------------------------
 * The assistant was originally only a tab on the run detail page. That is a fine place
 * for it when you are already reading a run — and completely undiscoverable from
 * anywhere else, which defeats the point of building it: the people who most need "what
 * is this record and what happens next" are the ones who have not yet drilled into a run.
 *
 * So the same component is reachable from every page here, and the two are kept
 * consistent rather than duplicated: this panel renders the exact same `RecordAssistant`,
 * and when the current route already identifies a run it opens straight onto that run
 * instead of asking the operator to pick the record they are visibly looking at.
 */
export function AssistantLauncher() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [picked, setPicked] = useState<string | null>(null);

  // `/decisions/R-web-1234` and `/runs/R-web-1234` both identify a run. Anything else
  // (the queue list, the overview, governance) does not, and falls through to the picker.
  const routeRunId = runIdFromPath(pathname);

  // Navigating to a different run while the panel is open should follow the operator, not
  // strand them on the record they opened it from. Adjust-during-render rather than an
  // effect, matching AppShell's own handling of the mobile drawer.
  const [lastRouteRunId, setLastRouteRunId] = useState(routeRunId);
  if (routeRunId !== lastRouteRunId) {
    setLastRouteRunId(routeRunId);
    setPicked(null);
  }

  const runId = picked ?? routeRunId;

  const close = useCallback(() => setOpen(false), []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, close]);

  return (
    <>
      {!open && (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="fixed bottom-5 right-5 z-40 inline-flex items-center gap-2 rounded-[var(--radius-full)] border border-transparent bg-[var(--brand)] px-4 py-2.5 text-[13px] font-medium text-white shadow-[var(--shadow-md)] transition-colors hover:bg-[var(--brand-hover)]"
        >
          <IconChat />
          Ask about a record
        </button>
      )}

      {open && (
        <aside
          role="dialog"
          aria-label="Record Assistant"
          className="fixed inset-x-0 bottom-0 z-40 flex max-h-[85dvh] flex-col border-t border-[var(--border-default)] bg-[var(--surface-raised)] shadow-[var(--shadow-lg)] sm:inset-x-auto sm:bottom-5 sm:right-5 sm:max-h-[min(46rem,85dvh)] sm:w-[26rem] sm:rounded-[var(--radius-lg)] sm:border"
        >
          <div className="flex shrink-0 items-center justify-between gap-2 border-b border-[var(--border-subtle)] px-4 py-2.5">
            <div className="flex min-w-0 items-center gap-2">
              <span aria-hidden="true" className="text-[var(--brand)]">
                <IconChat />
              </span>
              <span className="truncate text-[13px] font-semibold text-[var(--text-primary)]">
                Record Assistant
              </span>
            </div>
            <div className="flex shrink-0 items-center gap-1">
              {runId && (
                <Button variant="ghost" onClick={() => setPicked(null)} className="h-7 px-2">
                  {routeRunId && !picked ? "Other record" : "Back"}
                </Button>
              )}
              <button
                type="button"
                onClick={close}
                aria-label="Close the Record Assistant"
                className="rounded-[var(--radius-md)] px-2 py-1 text-[var(--text-tertiary)] hover:bg-[var(--surface-sunken)] hover:text-[var(--text-primary)]"
              >
                <span aria-hidden="true">✕</span>
              </button>
            </div>
          </div>

          {/* RecordAssistant caps its own next-steps list and chat log height and keeps
              its composer in normal document flow below both, so in the common case this
              wrapper never needs to scroll at all -- the composer stays visible without
              the operator hunting for it. overflow-y-auto stays on as a safety net for
              the rare case content still exceeds the panel (a very long next-steps list,
              a very short viewport), where nested scrolling is unremarkable. */}
          <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-4 py-3">
            {runId ? (
              // `key` remounts on a record change so the panel never shows the previous
              // record's answer under the new record's heading.
              <RecordAssistant key={runId} runId={runId} embedded />
            ) : (
              <RunPicker onPick={setPicked} />
            )}
          </div>
        </aside>
      )}
    </>
  );
}

/** `/decisions/<id>` and `/runs/<id>` identify a run; the list routes above them do not. */
function runIdFromPath(pathname: string): string | null {
  const match = /^\/(?:decisions|runs)\/([^/]+)\/?$/.exec(pathname);
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Debounce delay for the search-as-you-type request against `/api/runs`. Short enough
 * that typing still feels live, long enough that a normal typing cadence sends one
 * request per pause rather than one per keystroke.
 */
const SEARCH_DEBOUNCE_MS = 250;

/**
 * Type-to-find a record. No default browse list.
 *
 * An earlier version showed a static list here -- the pending queue plus the 8 most
 * recent decided runs -- open by default before anything was typed. Removed on request:
 * this system runs six workflows and keeps a full run history, so a fixed list is either
 * mostly-irrelevant noise standing between the operator and the search box, or (once the
 * pending queue is empty) nothing at all. Results now appear only once there's something
 * to search for -- a run id, batch id, or case id -- exactly like every other search box
 * in this product (Run History's own filter bar), not a second, different interaction to
 * learn.
 */
function RunPicker({ onPick }: { onPick: (runId: string) => void }) {
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(query.trim()), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [query]);

  const searching = debounced.length > 0;

  const queue = useApiResource((signal) => getQueue(undefined, signal), []);
  // The API's own `search` param does the matching server-side against run/subject ids,
  // so this is the same lookup Run History's filter bar performs -- not a client-side
  // re-implementation that could disagree with it. Only fetched once there's a query --
  // there is no "browse everything" state to keep in sync otherwise.
  const history = useApiResource(
    (signal) => getRunHistory({ search: debounced, limit: 8 }, signal),
    [debounced],
    { enabled: searching },
  );

  // The queue has no search endpoint of its own (it's the small, in-memory "what's
  // currently waiting" set -- see pending_queue.py), so it's filtered here against the
  // same query already sent to the server for run history. Substring, case-insensitive,
  // against exactly the two fields an operator would type: the run id and the subject id.
  const needle = debounced.toLowerCase();
  const pending = searching
    ? (queue.data ?? []).filter(
        (e) => e.run_id.toLowerCase().includes(needle) || e.subject_id.toLowerCase().includes(needle),
      )
    : [];
  const recent = (history.data?.items ?? []).filter(
    (run) => !pending.some((p) => p.run_id === run.run_id),
  );

  const loading = searching && ((queue.loading && !queue.data) || (history.loading && !history.data));
  const noResults = searching && !loading && pending.length === 0 && recent.length === 0;
  // Sorted into one flat, ranked list rather than two labelled sections: these are search
  // results now, not a browse view, and a pending run is simply the better match to lead
  // with -- it still holds its decision-support package (see the ordering note below).
  const results = [...pending.map((e) => ({ ...toResult(e) })), ...recent.map((r) => toResult(r))];

  return (
    <div className="space-y-3">
      <div>
        <label htmlFor="assistant-record-search" className="sr-only">
          Search for a record by run id, batch id, or case id
        </label>
        <div className="relative">
          <span
            aria-hidden="true"
            className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)]"
          >
            <IconSearch />
          </span>
          <input
            id="assistant-record-search"
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a run id, batch id, or case id…"
            className="h-9 w-full rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-raised)] py-1.5 pl-8 pr-3 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:border-[var(--border-strong)] focus:outline-none"
          />
        </div>
      </div>

      {!searching && (
        <p className="text-[13px] leading-relaxed text-[var(--text-tertiary)]">
          Type an id above to find a record and start asking about it.
        </p>
      )}

      {loading && <SkeletonText lines={3} />}

      {noResults && (
        <EmptyState
          title="No record matches that search"
          description={`Nothing pending or recorded matches "${debounced}". Check the id and try again.`}
        />
      )}

      {searching && !loading && results.length > 0 && (
        <ul className="space-y-1.5">
          {results.map((r) => (
            <RunButton key={r.runId} {...r} onPick={onPick} />
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * Common shape for a search result, from either source.
 *
 * A pending run still holds its decision-support package in memory, so the assistant can
 * describe its findings and evidence. A decided run cannot (the package lives in the
 * paused graph's state and is not copied to the audit store), and the assistant says so
 * rather than implying the run had no evidence -- so its note leads with that instead of
 * the terminal state, which the operator will see once inside the chat anyway.
 */
function toResult(entry: QueueEntry | { run_id: string; workflow: string; subject_id: string | null }) {
  if ("draft_summary" in entry) {
    const roles = entry.approver_roles ?? [];
    return {
      runId: entry.run_id,
      workflow: entry.workflow as Workflow,
      subjectId: entry.subject_id,
      tone: "pending" as const,
      note: roles.length > 0 ? `Awaiting ${roles.join(", ")}` : "Awaiting a decision",
    };
  }
  return {
    runId: entry.run_id,
    workflow: entry.workflow as Workflow,
    subjectId: entry.subject_id ?? entry.run_id,
    tone: "neutral" as const,
    note: "Decided — facts only, no findings package",
  };
}

function RunButton({
  runId,
  workflow,
  subjectId,
  tone,
  note,
  onPick,
}: {
  runId: string;
  workflow: Workflow;
  subjectId: string;
  tone: "pending" | "neutral";
  note?: string;
  onPick: (runId: string) => void;
}) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onPick(runId)}
        className="w-full rounded-[var(--radius-md)] border border-[var(--border-subtle)] px-3 py-2.5 text-left transition-colors hover:border-[var(--border-strong)] hover:bg-[var(--surface-sunken)]"
      >
        <span className="flex flex-wrap items-center gap-2">
          <Badge tone={tone} size="xs">
            {WORKFLOW_LABELS[workflow] ?? workflow}
          </Badge>
          <span className="font-mono text-[12px] font-medium text-[var(--text-primary)]">
            {WORKFLOW_SUBJECT_LABEL[workflow] ?? ""} {subjectId}
          </span>
        </span>
        {note && (
          <span className="mt-1 block truncate text-[12px] text-[var(--text-tertiary)]">
            {note}
          </span>
        )}
      </button>
    </li>
  );
}

function IconSearch() {
  return (
    <svg
      width={14}
      height={14}
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="7" cy="7" r="4.5" />
      <path d="m13.5 13.5-3-3" />
    </svg>
  );
}

function IconChat() {
  return (
    <svg
      width={16}
      height={16}
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M14 9.5a2 2 0 0 1-2 2H6l-3.5 2.5V4a2 2 0 0 1 2-2h7.5a2 2 0 0 1 2 2v5.5Z" />
      <path d="M5.5 5.5h5M5.5 8h3" />
    </svg>
  );
}
