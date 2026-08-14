import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * Data table.
 *
 * Wide content scrolls inside its own container -- the page body must never scroll
 * sideways. On small screens the caller renders cards instead (see `MobileCardList`);
 * a horizontally-scrolling table on a phone is technically responsive and practically
 * unusable.
 */
export function Table({
  children,
  caption,
  className,
}: {
  children: ReactNode;
  /** Screen-reader description of what the table contains. */
  caption: string;
  className?: string;
}) {
  return (
    <div className="overflow-x-auto">
      <table className={cn("w-full min-w-[40rem] border-collapse text-sm", className)}>
        <caption className="sr-only">{caption}</caption>
        {children}
      </table>
    </div>
  );
}

export function Th({
  children,
  className,
  sort,
  onSort,
  align = "left",
}: {
  children: ReactNode;
  className?: string;
  /** Current sort direction for this column, if it is the active one. */
  sort?: "asc" | "desc" | null;
  onSort?: () => void;
  align?: "left" | "right";
}) {
  return (
    <th
      scope="col"
      // aria-sort is what tells a screen reader the table is sorted and by which column.
      aria-sort={sort === "asc" ? "ascending" : sort === "desc" ? "descending" : undefined}
      className={cn(
        "border-b border-[var(--border-default)] bg-[var(--surface-sunken)] px-3 py-2",
        "text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]",
        align === "right" ? "text-right" : "text-left",
        className,
      )}
    >
      {onSort ? (
        <button
          type="button"
          onClick={onSort}
          className="inline-flex items-center gap-1 uppercase tracking-wider hover:text-[var(--text-primary)]"
        >
          {children}
          <span aria-hidden="true" className="text-[9px]">
            {sort === "asc" ? "▲" : sort === "desc" ? "▼" : "⇅"}
          </span>
        </button>
      ) : (
        children
      )}
    </th>
  );
}

export function Td({
  children,
  className,
  align = "left",
  mono = false,
}: {
  children: ReactNode;
  className?: string;
  align?: "left" | "right";
  mono?: boolean;
}) {
  return (
    <td
      className={cn(
        "border-b border-[var(--border-subtle)] px-3 py-2.5 align-middle text-[var(--text-primary)]",
        align === "right" && "text-right",
        mono && "font-mono text-[13px] tnum",
        className,
      )}
    >
      {children}
    </td>
  );
}

export function Tr({
  children,
  className,
  onClick,
}: {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}) {
  return (
    <tr
      onClick={onClick}
      className={cn(
        onClick && "cursor-pointer hover:bg-[var(--surface-sunken)]",
        "transition-colors",
        className,
      )}
    >
      {children}
    </tr>
  );
}

/**
 * The small-screen counterpart to a table. Rendered instead of, not alongside, the table
 * (Phase 22: convert tables into cards rather than shrinking them).
 */
export function MobileCardList({ children }: { children: ReactNode }) {
  return <ul className="divide-y divide-[var(--border-subtle)]">{children}</ul>;
}

export function Pagination({
  offset,
  limit,
  total,
  onChange,
}: {
  offset: number;
  limit: number;
  total: number;
  onChange: (offset: number) => void;
}) {
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + limit, total);
  const canPrev = offset > 0;
  const canNext = offset + limit < total;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--border-subtle)] px-4 py-3">
      <p className="text-xs text-[var(--text-tertiary)]">
        <span className="tnum">
          {from}–{to}
        </span>{" "}
        of <span className="tnum">{total}</span>
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={!canPrev}
          onClick={() => onChange(Math.max(0, offset - limit))}
          className="rounded-[var(--radius-md)] border border-[var(--border-default)] px-2.5 py-1 text-[13px] text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)] disabled:opacity-40 disabled:hover:bg-transparent"
        >
          ← Previous
        </button>
        <button
          type="button"
          disabled={!canNext}
          onClick={() => onChange(offset + limit)}
          className="rounded-[var(--radius-md)] border border-[var(--border-default)] px-2.5 py-1 text-[13px] text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)] disabled:opacity-40 disabled:hover:bg-transparent"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
