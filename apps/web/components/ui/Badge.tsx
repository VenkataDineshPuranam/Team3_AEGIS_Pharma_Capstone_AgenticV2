import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * Status badge.
 *
 * Every variant pairs a colour with a distinct GLYPH and a distinct WORD. Colour is never
 * the only carrier of meaning -- a user with a colour-vision deficiency, or reading a
 * greyscale print of an audit export, must still be able to tell "authoritative" from
 * "superseded" (Phase 28: non-colour status indicators).
 */

export type BadgeTone =
  | "ok"
  | "pending"
  | "blocked"
  | "abstained"
  | "refused"
  | "info"
  | "neutral"
  | "authoritative"
  | "draft-evidence"
  | "untrusted"
  | "superseded";

const TONE_STYLES: Record<BadgeTone, string> = {
  ok: "text-[var(--status-ok-fg)] bg-[var(--status-ok-bg)] border-[var(--status-ok-border)]",
  pending:
    "text-[var(--status-pending-fg)] bg-[var(--status-pending-bg)] border-[var(--status-pending-border)]",
  blocked:
    "text-[var(--status-blocked-fg)] bg-[var(--status-blocked-bg)] border-[var(--status-blocked-border)]",
  abstained:
    "text-[var(--status-abstained-fg)] bg-[var(--status-abstained-bg)] border-[var(--status-abstained-border)]",
  refused:
    "text-[var(--status-refused-fg)] bg-[var(--status-refused-bg)] border-[var(--status-refused-border)]",
  info: "text-[var(--status-info-fg)] bg-[var(--status-info-bg)] border-[var(--status-info-border)]",
  neutral: "text-[var(--text-secondary)] bg-[var(--surface-sunken)] border-[var(--border-default)]",
  authoritative:
    "text-[var(--evidence-authoritative-fg)] bg-[var(--evidence-authoritative-bg)] border-[var(--evidence-authoritative-border)]",
  "draft-evidence":
    "text-[var(--evidence-draft-fg)] bg-[var(--evidence-draft-bg)] border-[var(--evidence-draft-border)]",
  untrusted:
    "text-[var(--evidence-untrusted-fg)] bg-[var(--evidence-untrusted-bg)] border-[var(--evidence-untrusted-border)]",
  superseded:
    "text-[var(--evidence-superseded-fg)] bg-[var(--evidence-superseded-bg)] border-[var(--evidence-superseded-border)]",
};

/** The non-colour half of the signal. */
const TONE_GLYPHS: Record<BadgeTone, string> = {
  ok: "✓",
  pending: "◷",
  blocked: "■",
  abstained: "—",
  refused: "⊘",
  info: "i",
  neutral: "·",
  authoritative: "✓",
  "draft-evidence": "◐",
  untrusted: "✕",
  superseded: "⊗",
};

export function Badge({
  tone = "neutral",
  children,
  glyph = true,
  size = "sm",
  className,
  title,
}: {
  tone?: BadgeTone;
  children: ReactNode;
  glyph?: boolean;
  size?: "xs" | "sm";
  className?: string;
  title?: string;
}) {
  return (
    <span
      title={title}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-[var(--radius-full)] border font-medium whitespace-nowrap",
        size === "xs" ? "px-1.5 py-0.5 text-[10px]" : "px-2.5 py-0.5 text-xs",
        TONE_STYLES[tone],
        className,
      )}
    >
      {glyph && (
        <span aria-hidden="true" className="leading-none">
          {TONE_GLYPHS[tone]}
        </span>
      )}
      {children}
    </span>
  );
}

/**
 * A coloured dot for dense contexts (table rows, list items) where a full badge would be
 * too heavy. Always accompanied by adjacent text -- never the only indicator.
 */
export function StatusDot({ tone, className }: { tone: BadgeTone; className?: string }) {
  const colour: Record<BadgeTone, string> = {
    ok: "bg-[var(--status-ok-fg)]",
    pending: "bg-[var(--status-pending-fg)]",
    blocked: "bg-[var(--status-blocked-fg)]",
    abstained: "bg-[var(--status-abstained-fg)]",
    refused: "bg-[var(--status-refused-fg)]",
    info: "bg-[var(--status-info-fg)]",
    neutral: "bg-[var(--text-tertiary)]",
    authoritative: "bg-[var(--evidence-authoritative-fg)]",
    "draft-evidence": "bg-[var(--evidence-draft-fg)]",
    untrusted: "bg-[var(--evidence-untrusted-fg)]",
    superseded: "bg-[var(--evidence-superseded-fg)]",
  };
  return (
    <span
      aria-hidden="true"
      className={cn("inline-block size-1.5 shrink-0 rounded-full", colour[tone], className)}
    />
  );
}
