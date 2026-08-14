"use client";

import { useId, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

const CONTROL =
  "w-full rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-raised)] " +
  "px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] " +
  "hover:border-[var(--border-strong)] disabled:opacity-50";

/**
 * Every control here is label-associated via a generated id rather than by wrapping. Both
 * are valid HTML, but the explicit htmlFor/id pair is what keeps the association intact
 * when a field is later moved into a different layout -- and an approval form is not a
 * place to discover that a label came unhooked.
 */

export function Textarea({
  label,
  hint,
  error,
  required,
  className,
  ...rest
}: {
  label: string;
  hint?: ReactNode;
  error?: string | null;
  } & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const id = useId();
  const hintId = `${id}-hint`;
  const errorId = `${id}-error`;

  return (
    <div>
      <label htmlFor={id} className="block text-[13px] font-medium text-[var(--text-primary)]">
        {label}
        {required && (
          <span className="ml-1 text-[var(--status-blocked-fg)]" aria-hidden="true">
            *
          </span>
        )}
        {required && <span className="sr-only"> (required)</span>}
      </label>
      {hint && (
        <p id={hintId} className="mt-1 text-xs text-[var(--text-tertiary)]">
          {hint}
        </p>
      )}
      <textarea
        {...rest}
        id={id}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={cn(hint ? hintId : null, error ? errorId : null) || undefined}
        className={cn(
          CONTROL,
          "mt-1.5 min-h-24 resize-y leading-relaxed",
          error && "border-[var(--status-blocked-border)]",
          className,
        )}
      />
      {error && (
        <p id={errorId} role="alert" className="mt-1.5 text-xs text-[var(--status-blocked-fg)]">
          {error}
        </p>
      )}
    </div>
  );
}

export function Select({
  label,
  hint,
  hideLabel = false,
  className,
  children,
  ...rest
}: {
  label: string;
  hint?: ReactNode;
  /** Visually hidden but still announced -- for toolbar filters with obvious context. */
  hideLabel?: boolean;
  children: ReactNode;
} & SelectHTMLAttributes<HTMLSelectElement>) {
  const id = useId();
  return (
    <div className={cn(hideLabel && "contents")}>
      <label
        htmlFor={id}
        className={cn(
          hideLabel
            ? "sr-only"
            : "block text-[13px] font-medium text-[var(--text-primary)] mb-1.5",
        )}
      >
        {label}
      </label>
      <select {...rest} id={id} className={cn(CONTROL, "h-9 py-0 pr-8", className)}>
        {children}
      </select>
      {hint && !hideLabel && (
        <p className="mt-1 text-xs text-[var(--text-tertiary)]">{hint}</p>
      )}
    </div>
  );
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search…",
  label,
  className,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  label: string;
  className?: string;
}) {
  const id = useId();
  return (
    <div className={cn("relative", className)}>
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <span
        aria-hidden="true"
        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)]"
      >
        ⌕
      </span>
      <input
        id={id}
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={cn(CONTROL, "h-9 py-0 pl-8")}
      />
    </div>
  );
}

/**
 * Segmented filter control. Implemented as a radiogroup rather than a row of buttons so
 * arrow keys move between options, which is what a keyboard user expects from something
 * that looks like a segmented control.
 */
export function SegmentedControl<T extends string>({
  label,
  value,
  onChange,
  options,
  className,
}: {
  label: string;
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string; count?: number }[];
  className?: string;
}) {
  return (
    <div
      role="radiogroup"
      aria-label={label}
      className={cn(
        "inline-flex flex-wrap gap-0.5 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-sunken)] p-0.5",
        className,
      )}
    >
      {options.map((option) => {
        const active = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(option.value)}
            className={cn(
              "rounded-[var(--radius-sm)] px-2.5 py-1 text-[13px] font-medium transition-colors",
              active
                ? "bg-[var(--surface-raised)] text-[var(--text-primary)] shadow-[var(--shadow-sm)]"
                : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]",
            )}
          >
            {option.label}
            {option.count != null && (
              <span className="ml-1.5 tnum text-[var(--text-tertiary)]">{option.count}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
