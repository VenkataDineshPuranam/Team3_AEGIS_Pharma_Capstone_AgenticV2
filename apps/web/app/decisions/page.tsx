"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { PageBody, PageHeader } from "@/components/layout/AppShell";
import { useAuth } from "@/components/layout/AuthContext";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { SearchInput, SegmentedControl, Select } from "@/components/ui/Form";
import { EmptyState, ErrorState, Notice, SkeletonRows } from "@/components/ui/States";
import { Identifier, WorkflowChip } from "@/components/domain/Chips";
import { HitlTimerBadge } from "@/components/decisions/HitlTimerBadge";
import { useApiResource, useVisiblePolling } from "@/hooks/useApiResource";
import { getQueue, type QueueEntry, type Workflow } from "@/lib/api";
import { WORKFLOW_SUBJECT_LABEL, formatAge, formatDateTime } from "@/lib/format";

type WorkflowFilter = Workflow | "all";
type SortKey = "oldest" | "newest" | "workflow";

/**
 * Decision Queue — the primary operational page.
 *
 * Optimised for an expert who opens this many times a day: filtering and sorting are
 * client-side over an already-loaded queue (the pending set is small and in-memory on the
 * backend by design), so narrowing is instant and never round-trips.
 *
 * Rows are cards rather than table rows because each item carries five kinds of
 * information — workflow, subject, evidence weight, approval progress, and age — that a
 * flat table would flatten into indistinguishable columns.
 */
export default function DecisionQueuePage() {
  const { session } = useAuth();
  const role = session?.role ?? "";
  const pollMs = useVisiblePolling(10_000);
  const queue = useApiResource((s) => getQueue(undefined, s), [], { pollMs });

  const [workflow, setWorkflow] = useState<WorkflowFilter>("all");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<SortKey>("oldest");
  const [mineOnly, setMineOnly] = useState(false);

  const all = useMemo(() => queue.data ?? [], [queue.data]);

  const counts = useMemo(() => {
    const byWorkflow: Record<string, number> = {};
    for (const entry of all) byWorkflow[entry.workflow] = (byWorkflow[entry.workflow] ?? 0) + 1;
    return byWorkflow;
  }, [all]);

  const visible = useMemo(() => {
    let items = all;
    if (workflow !== "all") items = items.filter((e) => e.workflow === workflow);
    if (mineOnly) items = items.filter((e) => e.approver_roles.includes(role));
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      items = items.filter(
        (e) =>
          e.subject_id.toLowerCase().includes(q) ||
          e.run_id.toLowerCase().includes(q) ||
          (e.draft_summary ?? "").toLowerCase().includes(q) ||
          e.approver_roles.some((r) => r.toLowerCase().includes(q)),
      );
    }
    const sorted = [...items];
    if (sort === "oldest") sorted.sort((a, b) => a.created_at.localeCompare(b.created_at));
    else if (sort === "newest") sorted.sort((a, b) => b.created_at.localeCompare(a.created_at));
    else sorted.sort((a, b) => a.workflow.localeCompare(b.workflow) || a.created_at.localeCompare(b.created_at));
    return sorted;
  }, [all, workflow, search, sort, mineOnly, role]);

  const filtered = visible.length !== all.length;

  return (
    <>
      <PageHeader
        title="Decision Queue"
        description="Runs paused at a human-in-the-loop interrupt. Each one has passed evidence retrieval, the prohibited-action guard, and Critic verification — and cannot complete until an accountable human decides."
        actions={
          <>
            <span className="tnum text-[13px] text-[var(--text-tertiary)]">
              {queue.fetchedAt ? `Updated ${formatAge(queue.fetchedAt.toISOString())} ago` : ""}
            </span>
            <Button variant="secondary" onClick={queue.refresh} loading={queue.loading && !!all.length}>
              Refresh
            </Button>
          </>
        }
      />

      <PageBody className="space-y-4">
        {queue.error && all.length > 0 && (
          <Notice tone="warning" title="Showing the last successful load">
            {queue.error.userMessage} The list below may be out of date.
          </Notice>
        )}

        {/* --- toolbar --------------------------------------------------- */}
        <div className="flex flex-wrap items-center gap-2">
          <SegmentedControl<WorkflowFilter>
            label="Filter by workflow"
            value={workflow}
            onChange={setWorkflow}
            options={[
              { value: "all", label: "All", count: all.length },
              { value: "batch_review", label: "Batch", count: counts.batch_review ?? 0 },
              { value: "pv_intake", label: "PV", count: counts.pv_intake ?? 0 },
              { value: "supply_planning", label: "Supply", count: counts.supply_planning ?? 0 },
            ]}
          />

          <label className="inline-flex cursor-pointer items-center gap-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-raised)] px-2.5 py-1.5 text-[13px] text-[var(--text-secondary)]">
            <input
              type="checkbox"
              checked={mineOnly}
              onChange={(e) => setMineOnly(e.target.checked)}
              className="size-3.5 accent-[var(--brand)]"
            />
            Awaiting {role}
          </label>

          <SearchInput
            label="Search the decision queue"
            value={search}
            onChange={setSearch}
            placeholder="Subject, run id, summary or approver…"
            className="min-w-52 flex-1"
          />

          <Select
            label="Sort by"
            hideLabel
            value={sort}
            onChange={(e) => setSort(e.target.value as SortKey)}
            className="w-auto min-w-40"
          >
            <option value="oldest">Oldest first (longest waiting)</option>
            <option value="newest">Newest first</option>
            <option value="workflow">Group by workflow</option>
          </Select>
        </div>

        {/* --- list ------------------------------------------------------ */}
        {queue.error && all.length === 0 ? (
          <ErrorState
            message={queue.error.userMessage}
            hint={
              <>
                The Orchestrator API should be running at{" "}
                <code className="font-mono">
                  {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                </code>
                .
              </>
            }
            action={<Button onClick={queue.refresh}>Try again</Button>}
          />
        ) : queue.loading && all.length === 0 ? (
          <Card>
            <SkeletonRows rows={4} />
          </Card>
        ) : visible.length === 0 ? (
          <Card>
            {filtered || all.length === 0 ? (
              all.length === 0 ? (
                <EmptyState
                  title="Nothing is waiting for a decision"
                  description="Every governed workflow pauses here before it can complete, so an empty queue means no run is currently blocked on a human — not that the system is idle."
                  action={
                    <Link
                      href="/workflows"
                      className="inline-flex h-8 items-center rounded-[var(--radius-md)] border border-[var(--border-default)] px-3 text-[13px] font-medium hover:bg-[var(--surface-sunken)]"
                    >
                      Start a run
                    </Link>
                  }
                />
              ) : (
                <EmptyState
                  title="No items match these filters"
                  description={`${all.length} run${all.length === 1 ? " is" : "s are"} waiting, but none match the current workflow, role or search filters.`}
                  action={
                    <Button
                      onClick={() => {
                        setWorkflow("all");
                        setSearch("");
                        setMineOnly(false);
                      }}
                    >
                      Clear filters
                    </Button>
                  }
                />
              )
            ) : null}
          </Card>
        ) : (
          <>
            {filtered && (
              <p className="text-[13px] text-[var(--text-tertiary)]">
                Showing <span className="tnum font-medium">{visible.length}</span> of{" "}
                <span className="tnum">{all.length}</span>
              </p>
            )}
            <ul className="space-y-2.5">
              {visible.map((entry) => (
                <QueueRow key={entry.run_id} entry={entry} operatorRole={role} />
              ))}
            </ul>
          </>
        )}
      </PageBody>
    </>
  );
}

function QueueRow({ entry, operatorRole }: { entry: QueueEntry; operatorRole: string }) {
  const dualLeg = (entry.required_legs?.length ?? 0) > 1;
  const isMine = entry.approver_roles.includes(operatorRole);
  const citedIds = new Set(entry.draft_claims.flatMap((c) => c.cites));
  const uncited = entry.draft_claims.filter((c) => c.cites.length === 0).length;

  return (
    <li>
      <Card
        as="article"
        className="transition-colors hover:border-[var(--border-strong)] hover:shadow-[var(--shadow-md)]"
      >
        <Link
          href={`/decisions/${encodeURIComponent(entry.run_id)}`}
          className="block px-4 py-3.5 sm:px-5"
        >
          <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
            <div className="min-w-0 flex-1">
              {/* identity line */}
              <div className="flex flex-wrap items-center gap-2">
                <WorkflowChip workflow={entry.workflow} size="xs" />
                <span className="text-[11px] uppercase tracking-wider text-[var(--text-tertiary)]">
                  {WORKFLOW_SUBJECT_LABEL[entry.workflow]}
                </span>
                <span className="font-mono text-sm font-semibold text-[var(--text-primary)]">
                  {entry.subject_id}
                </span>
                {isMine && (
                  <Badge tone="info" size="xs">
                    Yours to decide
                  </Badge>
                )}
              </div>

              {/* summary */}
              <p className="mt-1.5 line-clamp-2 text-[13px] leading-relaxed text-[var(--text-secondary)]">
                {entry.draft_summary ?? (
                  <span className="italic">
                    No decision-support summary was produced for this run.
                  </span>
                )}
              </p>

              {/* signals */}
              <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-[11px] text-[var(--text-tertiary)]">
                <Identifier value={entry.run_id} className="text-[11px]" />
                <span aria-hidden="true">·</span>
                <span>
                  <span className="tnum font-medium text-[var(--text-secondary)]">
                    {entry.evidence.length}
                  </span>{" "}
                  evidence item{entry.evidence.length === 1 ? "" : "s"}
                </span>
                <span aria-hidden="true">·</span>
                <span>
                  <span className="tnum font-medium text-[var(--text-secondary)]">
                    {entry.draft_claims.length}
                  </span>{" "}
                  claim{entry.draft_claims.length === 1 ? "" : "s"}
                  {citedIds.size > 0 && ` citing ${citedIds.size}`}
                </span>
                {uncited > 0 && (
                  <>
                    <span aria-hidden="true">·</span>
                    <span className="text-[var(--status-pending-fg)]">
                      {uncited} uncited
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* right rail: waiting time/severity and approval state */}
            <div className="flex shrink-0 flex-col items-start gap-1.5 sm:items-end">
              <span title={formatDateTime(entry.created_at)}>
                <HitlTimerBadge timer={entry.hitl_timer} />
              </span>

              {dualLeg ? (
                <DualLegPill
                  approved={entry.approved_legs}
                  required={entry.required_legs ?? []}
                />
              ) : (
                <span className="max-w-44 truncate text-right text-[11px] text-[var(--text-tertiary)]">
                  {entry.approver_roles.join(", ")}
                </span>
              )}
            </div>
          </div>
        </Link>
      </Card>
    </li>
  );
}

/**
 * Dual-approval progress, in the queue.
 *
 * Phase 14's rule applies here as much as on the detail page: one approval must never
 * read as complete approval. So this shows "1 of 2" with the outstanding leg named —
 * never a single tick, and never a full-width green bar at 50%.
 */
function DualLegPill({ approved, required }: { approved: string[]; required: string[] }) {
  const outstanding = required.filter((leg) => !approved.includes(leg));
  const complete = outstanding.length === 0;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-[var(--radius-full)] border px-2 py-0.5 text-[11px] font-medium ${
        complete
          ? "border-[var(--status-ok-border)] bg-[var(--status-ok-bg)] text-[var(--status-ok-fg)]"
          : "border-[var(--status-pending-border)] bg-[var(--status-pending-bg)] text-[var(--status-pending-fg)]"
      }`}
      title={
        complete
          ? "Both approval legs recorded"
          : `Still awaiting: ${outstanding.join(", ")} leg`
      }
    >
      <span aria-hidden="true">{complete ? "✓" : "◷"}</span>
      <span className="tnum">
        {approved.length} of {required.length}
      </span>
      {!complete && <span>· {outstanding[0]} pending</span>}
    </span>
  );
}
