"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * Button.
 *
 * `danger` exists for rejection and veto. There is deliberately no "success"/green
 * variant for approval: an approval in this product is a considered, accountable act, and
 * styling it as the cheerful happy-path button is the wrong affordance for a control that
 * writes an irreversible record. Approve uses `primary`; the weight of the action is
 * carried by the confirmation dialog, not by colour.
 */

type Variant = "primary" | "secondary" | "ghost" | "danger" | "danger-strong";
type Size = "sm" | "md";

const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-[var(--brand)] text-white border-transparent hover:bg-[var(--brand-hover)] disabled:hover:bg-[var(--brand)]",
  secondary:
    "bg-[var(--surface-raised)] text-[var(--text-primary)] border-[var(--border-default)] hover:bg-[var(--surface-sunken)] hover:border-[var(--border-strong)]",
  ghost:
    "bg-transparent text-[var(--text-secondary)] border-transparent hover:bg-[var(--surface-sunken)] hover:text-[var(--text-primary)]",
  danger:
    "bg-[var(--surface-raised)] text-[var(--status-blocked-fg)] border-[var(--status-blocked-border)] hover:bg-[var(--status-blocked-bg)]",
  "danger-strong":
    "bg-[var(--status-blocked-fg)] text-white border-transparent hover:opacity-90",
};

const SIZES: Record<Size, string> = {
  sm: "h-8 px-3 text-[13px] gap-1.5",
  md: "h-9 px-4 text-sm gap-2",
};

export function Button({
  variant = "secondary",
  size = "sm",
  loading = false,
  loadingLabel = "Working…",
  children,
  className,
  disabled,
  ...rest
}: {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  loadingLabel?: string;
  children: ReactNode;
} & ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      // Screen readers are told the control is busy, not just visually dimmed.
      aria-busy={loading || undefined}
      className={cn(
        "inline-flex items-center justify-center rounded-[var(--radius-md)] border font-medium",
        "transition-colors duration-100",
        "disabled:opacity-45 disabled:cursor-not-allowed",
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
    >
      {loading && <Spinner />}
      {loading ? loadingLabel : children}
    </button>
  );
}

function Spinner() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 16 16"
      className="size-3.5 animate-spin"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <circle cx="8" cy="8" r="6" opacity="0.25" />
      <path d="M14 8a6 6 0 0 0-6-6" strokeLinecap="round" />
    </svg>
  );
}
