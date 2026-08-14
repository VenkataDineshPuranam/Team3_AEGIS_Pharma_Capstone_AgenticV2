import { cn } from "@/lib/cn";
import { Badge, type BadgeTone } from "@/components/ui/Badge";
import type { Workflow } from "@/lib/api";
import {
  TERMINAL_STATE_LABELS,
  WORKFLOW_SHORT,
  humanize,
  terminalStateTone,
  workflowTone,
} from "@/lib/format";

export function WorkflowChip({
  workflow,
  size = "sm",
}: {
  workflow: Workflow | string;
  size?: "xs" | "sm";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[var(--radius-full)] border font-medium whitespace-nowrap",
        size === "xs" ? "px-1.5 py-0.5 text-[10px]" : "px-2.5 py-0.5 text-xs",
        workflowTone(workflow),
      )}
    >
      {WORKFLOW_SHORT[workflow as Workflow] ?? humanize(workflow)}
    </span>
  );
}

export function StateBadge({
  state,
  size = "sm",
}: {
  state: string | null | undefined;
  size?: "xs" | "sm";
}) {
  if (!state) return <Badge tone="neutral" size={size}>Unknown</Badge>;
  return (
    <Badge tone={terminalStateTone(state)} size={size}>
      {TERMINAL_STATE_LABELS[state] ?? humanize(state)}
    </Badge>
  );
}

/** Monospace identifier with a copy affordance -- run ids get read aloud and pasted. */
export function Identifier({
  value,
  className,
  title,
}: {
  value: string;
  className?: string;
  title?: string;
}) {
  return (
    <span
      title={title ?? value}
      className={cn("font-mono text-[13px] tnum text-[var(--text-secondary)]", className)}
    >
      {value}
    </span>
  );
}

/**
 * The product's most important recurring statement.
 *
 * Placed wherever a user could otherwise read a finding as an instruction. It is a
 * component rather than repeated prose so the wording cannot drift into something softer
 * on one screen than another.
 */
export function DecisionSupportNotice({ className }: { className?: string }) {
  return (
    <p
      className={cn(
        "rounded-[var(--radius-md)] border border-[var(--status-info-border)] bg-[var(--status-info-bg)] px-3 py-2 text-[12px] leading-relaxed text-[var(--text-secondary)]",
        className,
      )}
    >
      <strong className="text-[var(--status-info-fg)]">Decision support only.</strong> AEGIS
      produces findings and options for a human to judge. It does not make, recommend, or
      execute the terminal decision — that authority remains entirely with the accountable
      person named below.
    </p>
  );
}

export function toneForDependency(status: string): BadgeTone {
  switch (status) {
    case "ok":
      return "ok";
    case "degraded":
      return "pending";
    case "unavailable":
      return "blocked";
    case "not_configured":
      return "neutral";
    default:
      return "neutral";
  }
}
