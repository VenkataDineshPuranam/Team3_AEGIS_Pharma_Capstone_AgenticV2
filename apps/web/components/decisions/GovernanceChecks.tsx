"use client";

import { Badge, type BadgeTone } from "@/components/ui/Badge";
import { Notice } from "@/components/ui/States";
import type { AuditedRun, HumanAction, QueueEntry, Workflow } from "@/lib/api";
import { ABSTENTION_EXPLANATIONS, WORKFLOW_BOUNDARY, humanize } from "@/lib/format";

/**
 * Which deterministic controls ran, and what they concluded.
 *
 * This is a report, not an evaluation: nothing here is computed by the browser. Each row
 * is stated only when the run's own recorded state proves it. A run that is paused at its
 * HITL interrupt has, by the shape of the graph, necessarily passed policy load, evidence
 * retrieval, the evidence gate, both guard passes and the Critic — there is no edge that
 * reaches an interrupt otherwise. Where the state cannot prove a control's outcome, the
 * row says "not recorded" rather than assuming it passed.
 */
export function GovernanceChecks({
  workflow,
  entry,
  audit,
  humanActions,
}: {
  workflow: Workflow;
  entry: QueueEntry | null;
  audit: AuditedRun | null;
  humanActions: HumanAction[];
}) {
  const paused = entry !== null;
  const blocked = audit?.terminal_state === "blocked";
  const refused = audit?.terminal_state === "refused";
  const abstained = audit?.terminal_state === "abstained";
  const boundary = WORKFLOW_BOUNDARY[workflow];

  const checks: {
    name: string;
    outcome: string;
    tone: BadgeTone;
    detail: string;
  }[] = [];

  // Policy load -- provable from the recorded policy version, or from being paused.
  checks.push(
    audit?.policy_contract_version
      ? {
          name: "Policy contract loaded",
          outcome: `v${audit.policy_contract_version.replace(/^v/, "")}`,
          tone: "ok",
          detail:
            "The versioned prohibition contract was loaded before any tool ran. An unreadable policy makes the run refuse — there is no cached-policy fallback.",
        }
      : refused && audit?.abstention_reason === "fail_closed"
        ? {
            name: "Policy contract loaded",
            outcome: "Failed closed",
            tone: "blocked",
            detail:
              "The policy contract could not be loaded, so the run refused rather than proceed on a stale or default policy.",
          }
        : paused
          ? {
              name: "Policy contract loaded",
              outcome: "Passed",
              tone: "ok",
              detail:
                "The run reached its human-in-the-loop interrupt, which is unreachable without a loaded policy contract.",
            }
          : {
              name: "Policy contract loaded",
              outcome: "Not recorded",
              tone: "neutral",
              detail: "This run predates the recording of policy version in the audit store.",
            },
  );

  // Evidence authority.
  const evidenceCount = entry?.evidence.length ?? audit?.evidence_ids?.length ?? null;
  checks.push({
    name: "Evidence authority enforced",
    outcome:
      evidenceCount === null
        ? "Not recorded"
        : `${evidenceCount} citable item${evidenceCount === 1 ? "" : "s"}`,
    tone: evidenceCount === null ? "neutral" : evidenceCount > 0 ? "ok" : "pending",
    detail:
      "Untrusted and superseded documents are filtered inside the retrieval query itself. No code path returns one to a run, so every item attached here is citable by construction.",
  });

  // Evidence gate.
  if (abstained && audit?.abstention_reason === "insufficient_evidence") {
    checks.push({
      name: "Evidence sufficiency gate",
      outcome: "Abstained",
      tone: "abstained",
      detail:
        "No citable evidence was found even after the one permitted scope-preserving broadening. The run abstained rather than answer unsupported.",
    });
  } else if (paused || audit?.terminal_state === "completed") {
    checks.push({
      name: "Evidence sufficiency gate",
      outcome: "Sufficient",
      tone: "ok",
      detail:
        "A second, independent check over the retrieved set as a whole — catching a wrongly-filtered list that would still type-check per item.",
    });
  }

  // Prohibited-action guard.
  checks.push(
    blocked
      ? {
          name: "Prohibited-action guard",
          outcome: "Blocked",
          tone: "blocked",
          detail:
            audit?.abstention_reason === "prohibition_adjacent"
              ? "The Critic judged the draft adjacent to a prohibited action. This is never retried — retrying would ask the model to rephrase a near-miss on the highest-severity control."
              : "Generated text matched a prohibited term for this workflow. The output was stopped before any human saw it.",
        }
      : paused || audit?.terminal_state === "completed"
        ? {
            name: "Prohibited-action guard",
            outcome: "Cleared (twice)",
            tone: "ok",
            detail:
              "The guard runs before the Critic and again after it. Both passes cleared. It pattern-matches the output shape; it never asks the model whether its own output is acceptable.",
          }
        : {
            name: "Prohibited-action guard",
            outcome: "Not reached",
            tone: "neutral",
            detail: "The run ended before any text was generated.",
          },
  );

  // Critic.
  if (paused || audit?.terminal_state === "completed") {
    checks.push({
      name: "Critic verification",
      outcome: "Approved for human",
      tone: "ok",
      detail:
        "An independent verification pass. A rejection carries a closed-enum reason code; only a distinct, retryable code permits one more synthesis attempt.",
    });
  } else if (abstained && audit?.abstention_reason === "cap_exceeded") {
    checks.push({
      name: "Critic verification",
      outcome: "Cap exceeded",
      tone: "abstained",
      detail:
        "The run reached its ceiling of 6 model calls without the Critic approving an output. Treated as an engineering defect, not a domain conclusion.",
    });
  }

  // HITL.
  checks.push({
    name: "Human-in-the-loop routing",
    outcome: paused
      ? "Awaiting decision"
      : humanActions.length > 0
        ? `${humanActions.length} action${humanActions.length === 1 ? "" : "s"} recorded`
        : audit?.abstention_reason === "hitl_timeout"
          ? "Expired — no action"
          : "Not reached",
    tone: paused
      ? "pending"
      : humanActions.length > 0
        ? "ok"
        : audit?.abstention_reason === "hitl_timeout"
          ? "abstained"
          : "neutral",
    detail:
      workflow === "supply_planning"
        ? "Dual approval: both the planning and quality legs are required. One leg approving is not approval, and an expiry with one leg outstanding takes no action."
        : workflow === "pv_intake"
          ? "Every PV output routes to a human — there is no lower-risk skip path. The Patient Safety Representative's veto can be registered at any tier and cannot be overridden."
          : "Every output routes to a named, accountable approver. A timeout is never an implicit approval.",
  });

  return (
    <div className="space-y-4">
      <p className="text-[13px] leading-relaxed text-[var(--text-secondary)]">
        These controls are enforced by the backend graph and policy engine. This panel
        reports what they concluded for this run; it evaluates nothing itself.
      </p>

      <ul className="space-y-2">
        {checks.map((check) => (
          <li
            key={check.name}
            className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] px-3.5 py-3"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-[13px] font-medium text-[var(--text-primary)]">
                {check.name}
              </span>
              <Badge tone={check.tone} size="xs">
                {check.outcome}
              </Badge>
            </div>
            <p className="mt-1.5 text-[12px] leading-relaxed text-[var(--text-secondary)]">
              {check.detail}
            </p>
          </li>
        ))}
      </ul>

      {audit?.abstention_reason && ABSTENTION_EXPLANATIONS[audit.abstention_reason] && (
        <Notice
          tone={blocked || refused ? "blocked" : "warning"}
          title={`Outcome: ${humanize(audit.abstention_reason)}`}
        >
          {ABSTENTION_EXPLANATIONS[audit.abstention_reason]}
        </Notice>
      )}

      <div className="rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-sunken)] px-3.5 py-3">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
          Structural prohibitions for this workflow
        </p>
        <ul className="mt-2 space-y-1">
          {boundary.neverDoes.map((item) => (
            <li key={item} className="flex items-start gap-2 text-[12px] text-[var(--text-secondary)]">
              <span aria-hidden="true" className="mt-px text-[var(--status-blocked-fg)]">
                ⊘
              </span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
