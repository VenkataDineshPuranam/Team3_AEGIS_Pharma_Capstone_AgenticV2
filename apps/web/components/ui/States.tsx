import type { ReactNode } from "react";
import { cn } from "@/lib/cn";
import { Card } from "./Card";

/**
 * Loading / empty / error / blocked states.
 *
 * Phase 23's requirement is that no screen is ever blank and no state is ever unexplained.
 * These are components rather than ad-hoc markup so that "explain why there is nothing
 * here" is the path of least resistance on every screen.
 */

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton", className)} aria-hidden="true" />;
}

/**
 * Skeletons are decorative -- the live region is what actually tells a screen-reader user
 * that something is loading. Without it, a blind user hears silence during every fetch.
 */
export function LoadingRegion({ label = "Loading" }: { label?: string }) {
  return (
    <span role="status" aria-live="polite" className="sr-only">
      {label}
    </span>
  );
}

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn("space-y-2", className)} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton h-3"
          style={{ width: i === lines - 1 ? "60%" : `${88 - i * 6}%` }}
        />
      ))}
    </div>
  );
}

export function SkeletonRows({ rows = 5 }: { rows?: number }) {
  return (
    <div className="divide-y divide-[var(--border-subtle)]">
      <LoadingRegion />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 px-4 py-4" aria-hidden="true">
          <div className="skeleton size-2 rounded-full" />
          <div className="skeleton h-3 w-24" />
          <div className="skeleton h-3 flex-1" />
          <div className="skeleton h-3 w-16" />
        </div>
      ))}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
  icon,
}: {
  title: string;
  /** Always explain WHY it is empty -- not merely that it is. */
  description: ReactNode;
  action?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-14 text-center">
      {icon && <div className="mb-3 text-[var(--text-tertiary)]">{icon}</div>}
      <p className="text-sm font-medium text-[var(--text-primary)]">{title}</p>
      <p className="mt-1.5 max-w-md text-sm text-[var(--text-secondary)]">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  message,
  hint,
  action,
  className,
}: {
  title?: string;
  message: string;
  /** What the user can actually do about it. An error without a next step is a dead end. */
  hint?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn("border-[var(--status-blocked-border)] bg-[var(--status-blocked-bg)]", className)}>
      <div className="px-4 py-4 sm:px-5">
        <div className="flex items-start gap-3">
          <span aria-hidden="true" className="mt-0.5 text-[var(--status-blocked-fg)]">
            ⚠
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-[var(--status-blocked-fg)]">{title}</p>
            {/* role="alert" announces the failure without the user having to hunt for it. */}
            <p role="alert" className="mt-1 text-sm break-words text-[var(--text-primary)]">
              {message}
            </p>
            {hint && <p className="mt-2 text-xs text-[var(--text-secondary)]">{hint}</p>}
            {action && <div className="mt-3">{action}</div>}
          </div>
        </div>
      </div>
    </Card>
  );
}

/**
 * An explanatory panel for a governed state -- blocked, expired, partially approved.
 *
 * Distinct from ErrorState on purpose: a governance block is the system working correctly,
 * and presenting it as a malfunction would teach users to treat controls as bugs.
 */
export function Notice({
  tone = "info",
  title,
  children,
  className,
}: {
  tone?: "info" | "warning" | "blocked" | "ok";
  title: ReactNode;
  children?: ReactNode;
  className?: string;
}) {
  const styles = {
    info: "border-[var(--status-info-border)] bg-[var(--status-info-bg)] text-[var(--status-info-fg)]",
    warning:
      "border-[var(--status-pending-border)] bg-[var(--status-pending-bg)] text-[var(--status-pending-fg)]",
    blocked:
      "border-[var(--status-blocked-border)] bg-[var(--status-blocked-bg)] text-[var(--status-blocked-fg)]",
    ok: "border-[var(--status-ok-border)] bg-[var(--status-ok-bg)] text-[var(--status-ok-fg)]",
  }[tone];
  const glyph = { info: "i", warning: "!", blocked: "■", ok: "✓" }[tone];

  return (
    <div className={cn("rounded-[var(--radius-md)] border px-3.5 py-3", styles, className)}>
      <div className="flex items-start gap-2.5">
        <span aria-hidden="true" className="mt-px text-xs font-bold">
          {glyph}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-[13px] font-semibold">{title}</p>
          {children && (
            <div className="mt-1 text-[13px] leading-relaxed text-[var(--text-secondary)]">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
