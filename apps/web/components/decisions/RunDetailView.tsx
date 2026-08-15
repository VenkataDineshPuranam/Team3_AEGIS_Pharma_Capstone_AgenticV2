"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageBody, PageHeader } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader, Field } from "@/components/ui/Card";
import { Tabs } from "@/components/ui/Tabs";
import { ErrorState, Notice, SkeletonText } from "@/components/ui/States";
import { RecordAssistant } from "@/components/assistant/RecordAssistant";
import { AuditTimeline } from "@/components/audit/AuditTimeline";
import { ApprovalPanel } from "@/components/decisions/ApprovalPanel";
import { DecisionSupport } from "@/components/decisions/DecisionSupport";
import { DomainFindings } from "@/components/decisions/DomainFindings";
import { GovernanceChecks } from "@/components/decisions/GovernanceChecks";
import { HitlTimerBadge } from "@/components/decisions/HitlTimerBadge";
import { Identifier, WorkflowChip } from "@/components/domain/Chips";
import { useApiResource } from "@/hooks/useApiResource";
import { getRun, type Workflow } from "@/lib/api";
import { WORKFLOW_LABELS, WORKFLOW_SUBJECT_LABEL, formatDateTime } from "@/lib/format";

type Tab = "support" | "findings" | "governance" | "audit" | "assistant";

/**
 * Decision workspace.
 *
 * Two columns on wide screens: the investigation on the left, the action on the right,
 * with the action panel sticky so an approver never has to scroll away from the evidence
 * to act on it. Below `xl` it stacks with the action last — you should read before you
 * decide, and on a narrow screen the reading order is the layout.
 */
export function RunDetailView({
  runId,
  backHref,
  backLabel,
  /** Where to send the user after a decision is recorded. */
  afterDecideHref = "/decisions",
}: {
  runId: string;
  backHref: string;
  backLabel: string;
  afterDecideHref?: string;
}) {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("support");

  const run = useApiResource((s) => getRun(decodeURIComponent(runId), s), [runId]);
  const detail = run.data;
  const entry = detail?.pending ?? null;
  const workflow = (entry?.workflow ?? detail?.audit?.workflow) as Workflow | undefined;

  if (run.error) {
    return (
      <>
        <PageHeader title="Decision" breadcrumb={<Breadcrumb href={backHref} label={backLabel} />} />
        <PageBody>
          <ErrorState
            title={run.error.status === 404 ? "This run is not available" : "Could not load the run"}
            message={
              run.error.status === 404
                ? "No run with this id is pending or recorded. It may have been decided in a previous session — the pending queue is in-memory and does not survive an API restart."
                : run.error.userMessage
            }
            action={
              <Link
                href={backHref}
                className="inline-flex h-8 items-center rounded-[var(--radius-md)] border border-[var(--border-default)] px-3 text-[13px] font-medium hover:bg-[var(--surface-sunken)]"
              >
                {backLabel}
              </Link>
            }
          />
        </PageBody>
      </>
    );
  }

  if (run.loading && !detail) {
    return (
      <>
        <PageHeader title="Loading decision…" breadcrumb={<Breadcrumb href={backHref} label={backLabel} />} />
        <PageBody>
          <Card>
            <CardBody>
              <SkeletonText lines={8} />
            </CardBody>
          </Card>
        </PageBody>
      </>
    );
  }

  if (!detail) return null;

  const decided = !detail.decision_support_available;

  return (
    <>
      <PageHeader
        breadcrumb={<Breadcrumb href={backHref} label={backLabel} />}
        title={
          entry
            ? `${WORKFLOW_SUBJECT_LABEL[entry.workflow]} ${entry.subject_id}`
            : (detail.audit?.subject_id ?? detail.run_id)
        }
        description={
          <span className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
            {workflow && <WorkflowChip workflow={workflow} />}
            {workflow && <span>{WORKFLOW_LABELS[workflow]}</span>}
            <Identifier value={detail.run_id} />
            {entry && <HitlTimerBadge timer={entry.hitl_timer} />}
          </span>
        }
        actions={
          <Button variant="secondary" onClick={run.refresh} loading={run.loading}>
            Refresh
          </Button>
        }
      />

      <PageBody>
        {decided && (
          <Notice tone="info" className="mb-5" title="This run is no longer awaiting a decision">
            {detail.decision_support_unavailable_reason}
          </Notice>
        )}

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
          {/* --- investigation ------------------------------------------ */}
          <div className="min-w-0">
            <Card>
              <CardBody padded={false}>
                <div className="px-4 sm:px-5">
                  <Tabs<Tab>
                    label="Decision detail sections"
                    value={tab}
                    onChange={setTab}
                    tabs={[
                      { value: "support", label: "Decision support" },
                      {
                        value: "findings",
                        label: "Structured findings",
                      },
                      { value: "governance", label: "Governance" },
                      { value: "audit", label: "Audit", count: detail.timeline.length },
                      { value: "assistant", label: "Assistant" },
                    ]}
                  >
                    <div className="pb-5">
                      {tab === "support" &&
                        (entry ? (
                          <DecisionSupport entry={entry} />
                        ) : (
                          <UnavailablePanel reason={detail.decision_support_unavailable_reason} />
                        ))}

                      {tab === "findings" &&
                        (entry && workflow ? (
                          <DomainFindings workflow={workflow} payload={entry.domain_payload} />
                        ) : (
                          <UnavailablePanel reason={detail.decision_support_unavailable_reason} />
                        ))}

                      {tab === "governance" && workflow && (
                        <GovernanceChecks
                          workflow={workflow}
                          entry={entry}
                          audit={detail.audit}
                          humanActions={detail.human_actions}
                        />
                      )}

                      {tab === "audit" && <AuditTimeline events={detail.timeline} />}

                      {/* Mounted only while its tab is selected: opening the panel costs
                          a model call, and a background tab quietly spending tokens on a
                          page nobody is reading is exactly what the denial-of-wallet
                          guardrail exists to prevent. */}
                      {tab === "assistant" && (
                        <div className="pt-4">
                          <RecordAssistant key={detail.run_id} runId={detail.run_id} embedded />
                        </div>
                      )}
                    </div>
                  </Tabs>
                </div>
              </CardBody>
            </Card>
          </div>

          {/* --- action ------------------------------------------------- */}
          <div className="min-w-0">
            <div className="xl:sticky xl:top-6 space-y-5">
              <Card>
                <CardHeader
                  title={entry ? "Human decision required" : "Recorded outcome"}
                  description={
                    entry
                      ? "This run cannot complete until an accountable human decides."
                      : "What was recorded for this run."
                  }
                />
                <CardBody>
                  {entry ? (
                    <ApprovalPanel
                      entry={entry}
                      onDecided={() => {
                        run.refresh();
                        router.push(afterDecideHref);
                      }}
                    />
                  ) : (
                    <RecordedOutcome detail={detail} />
                  )}
                </CardBody>
              </Card>

              {/* Run facts, always available regardless of pending state. */}
              <Card>
                <CardHeader title="Run" level={3} />
                <CardBody>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-3.5">
                    <Field label="Run id" mono>
                      {detail.run_id}
                    </Field>
                    {detail.audit?.trace_id && (
                      <Field label="Trace id" mono>
                        {detail.audit.trace_id}
                      </Field>
                    )}
                    {entry && <Field label="Requested by">{entry.requester_role}</Field>}
                    {entry && (
                      <Field label="Submitted">{formatDateTime(entry.created_at)}</Field>
                    )}
                    {detail.audit && (
                      <>
                        <Field label="Policy version" mono>
                          {detail.audit.policy_contract_version ?? "—"}
                        </Field>
                        <Field label="Model calls" mono>
                          {detail.audit.llm_calls ?? "—"}
                        </Field>
                        <Field label="Tokens" mono>
                          {detail.audit.tokens_in != null
                            ? `${detail.audit.tokens_in} in / ${detail.audit.tokens_out} out`
                            : "—"}
                        </Field>
                        <Field label="Finalized">
                          {formatDateTime(detail.audit.recorded_at)}
                        </Field>
                      </>
                    )}
                  </dl>
                </CardBody>
              </Card>
            </div>
          </div>
        </div>
      </PageBody>
    </>
  );
}

function Breadcrumb({ href, label }: { href: string; label: string }) {
  return (
    <nav aria-label="Breadcrumb">
      <Link
        href={href}
        className="text-[13px] text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
      >
        ← {label}
      </Link>
    </nav>
  );
}

function UnavailablePanel({ reason }: { reason: string | null }) {
  return (
    <Notice tone="info" title="Decision-support package unavailable">
      {reason ??
        "This run's decision-support package is not available. The audit record and timeline remain complete."}
    </Notice>
  );
}

function RecordedOutcome({
  detail,
}: {
  detail: NonNullable<ReturnType<typeof useApiResource<Awaited<ReturnType<typeof getRun>>>>["data"]>;
}) {
  const veto = detail.human_actions.find((a) => a.action === "veto_registered");

  return (
    <div className="space-y-4">
      {veto && (
        <div className="rounded-[var(--radius-md)] border-2 border-[var(--status-blocked-border)] bg-[var(--status-blocked-bg)] p-3.5">
          <p className="text-sm font-bold uppercase tracking-wide text-[var(--status-blocked-fg)]">
            ⊘ Vetoed
          </p>
          <p className="mt-1.5 text-[13px] text-[var(--text-primary)]">
            {veto.role} registered a patient safety veto. The governed state is{" "}
            <strong>rejected</strong>, and this cannot be overridden by any later approval.
          </p>
          <blockquote className="mt-2 border-l-2 border-[var(--status-blocked-border)] pl-2.5 text-[13px] italic text-[var(--text-secondary)]">
            {veto.justification}
          </blockquote>
        </div>
      )}

      {detail.audit ? (
        <dl className="space-y-3">
          <Field label="Terminal state">
            <Badge
              tone={
                detail.audit.terminal_state === "completed"
                  ? "ok"
                  : detail.audit.terminal_state === "blocked"
                    ? "blocked"
                    : "abstained"
              }
            >
              {detail.audit.terminal_state}
            </Badge>
          </Field>
          {detail.audit.hitl_status && (
            <Field label="Human decision">{detail.audit.hitl_status}</Field>
          )}
        </dl>
      ) : (
        <p className="text-[13px] text-[var(--text-tertiary)]">
          No audit record exists for this run yet.
        </p>
      )}

      {detail.human_actions.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
            Human actions recorded
          </p>
          <ul className="mt-2 space-y-2.5">
            {detail.human_actions.map((action, i) => (
              <li
                key={i}
                className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] px-3 py-2.5"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Badge
                    tone={
                      action.action === "approved"
                        ? "ok"
                        : action.action === "veto_registered"
                          ? "blocked"
                          : "pending"
                    }
                    size="xs"
                  >
                    {action.action}
                  </Badge>
                  <span className="text-[12px] font-medium text-[var(--text-primary)]">
                    {action.role}
                  </span>
                </div>
                <p className="mt-1.5 text-[13px] leading-relaxed text-[var(--text-secondary)]">
                  {action.justification}
                </p>
                <p className="mt-1 tnum text-[11px] text-[var(--text-tertiary)]">
                  {formatDateTime(action.recorded_at)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
