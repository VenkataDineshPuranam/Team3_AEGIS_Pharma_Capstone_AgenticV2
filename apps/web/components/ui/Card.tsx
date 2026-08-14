import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

export function Card({
  children,
  className,
  as: Tag = "div",
}: {
  children: ReactNode;
  className?: string;
  as?: "div" | "section" | "article" | "li";
}) {
  return (
    <Tag
      className={cn(
        "rounded-[var(--radius-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] shadow-[var(--shadow-sm)]",
        className,
      )}
    >
      {children}
    </Tag>
  );
}

export function CardHeader({
  title,
  description,
  actions,
  level = 2,
  className,
}: {
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  /** Heading level -- set explicitly so each page keeps a correct outline (Phase 28). */
  level?: 2 | 3 | 4;
  className?: string;
}) {
  const Heading = `h${level}` as "h2" | "h3" | "h4";
  return (
    <div
      className={cn(
        "flex flex-wrap items-start justify-between gap-3 border-b border-[var(--border-subtle)] px-4 py-3 sm:px-5",
        className,
      )}
    >
      <div className="min-w-0">
        <Heading className="text-sm font-semibold tracking-tight text-[var(--text-primary)]">
          {title}
        </Heading>
        {description && (
          <p className="mt-0.5 text-xs text-[var(--text-tertiary)]">{description}</p>
        )}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </div>
  );
}

export function CardBody({
  children,
  className,
  padded = true,
}: {
  children: ReactNode;
  className?: string;
  padded?: boolean;
}) {
  return <div className={cn(padded && "px-4 py-4 sm:px-5", className)}>{children}</div>;
}

/**
 * Label/value pair. The workhorse of this product: most screens are dense factual
 * readouts, and consistent alignment is what makes them scannable.
 */
export function Field({
  label,
  children,
  mono = false,
  className,
}: {
  label: ReactNode;
  children: ReactNode;
  mono?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("min-w-0", className)}>
      <dt className="text-[11px] font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
        {label}
      </dt>
      <dd
        className={cn(
          "mt-1 text-sm text-[var(--text-primary)] break-words",
          mono && "font-mono text-[13px] tnum",
        )}
      >
        {children}
      </dd>
    </div>
  );
}

/**
 * The single approved way to render a value the backend did not provide.
 *
 * Phase 5's rule -- show "Not available" rather than fake data -- only holds if there is
 * one obvious component to reach for. A dash rendered inline is how a placeholder quietly
 * becomes indistinguishable from a real zero.
 */
export function NotAvailable({ reason }: { reason?: string }) {
  return (
    <span
      className="text-[var(--text-tertiary)] italic"
      title={reason ?? "This value is not available from the backend."}
    >
      Not available
    </span>
  );
}

/** Value that is legitimately absent because nothing happened -- distinct from unknown. */
export function NotRecorded({ reason }: { reason?: string }) {
  return (
    <span
      className="text-[var(--text-tertiary)] italic"
      title={reason ?? "No record of this exists in the audit store."}
    >
      Not recorded
    </span>
  );
}
