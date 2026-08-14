"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * Modal dialog.
 *
 * Built on the native <dialog> element rather than a portal + div stack, because the
 * platform already implements the parts that are easy to get wrong: the top layer, the
 * backdrop, inert-ing the page behind it, Escape-to-close, and initial focus containment.
 *
 * What this component still has to do itself:
 *   - restore focus to the element that opened it (browsers vary on this)
 *   - close on backdrop click, without swallowing clicks inside the panel
 *   - block the Escape key while a submission is in flight, so a half-sent approval
 *     cannot be dismissed into an unknown state
 */
export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  /** While true, the dialog cannot be dismissed -- a mutation is in flight. */
  busy = false,
  size = "md",
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  busy?: boolean;
  size?: "md" | "lg";
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const opener = useRef<Element | null>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    if (open && !node.open) {
      opener.current = document.activeElement;
      node.showModal();
    } else if (!open && node.open) {
      node.close();
      // Return focus to whatever opened the dialog. Without this, keyboard focus falls
      // back to <body> and the user loses their place in the queue they came from.
      if (opener.current instanceof HTMLElement) opener.current.focus();
    }
  }, [open]);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const onCancel = (e: Event) => {
      // `cancel` fires on Escape. Refusing it while busy prevents dismissing a dialog
      // whose request has already been sent.
      if (busy) e.preventDefault();
      else onClose();
    };
    node.addEventListener("cancel", onCancel);
    return () => node.removeEventListener("cancel", onCancel);
  }, [busy, onClose]);

  return (
    <dialog
      ref={ref}
      aria-labelledby="dialog-title"
      className={cn(
        "m-auto w-[calc(100vw-2rem)] rounded-[var(--radius-lg)] border border-[var(--border-default)]",
        "bg-[var(--surface-overlay)] p-0 text-[var(--text-primary)] shadow-[var(--shadow-lg)]",
        "backdrop:bg-black/40 backdrop:backdrop-blur-[1px] open:animate-slide-up",
        size === "lg" ? "max-w-2xl" : "max-w-lg",
      )}
      onClick={(e) => {
        // A click landing on the <dialog> itself is a backdrop click: the panel below
        // stops propagation, so anything reaching here was outside it.
        if (e.target === ref.current && !busy) onClose();
      }}
    >
      <div onClick={(e) => e.stopPropagation()}>
        <div className="border-b border-[var(--border-subtle)] px-5 py-4">
          <h2 id="dialog-title" className="text-base font-semibold tracking-tight">
            {title}
          </h2>
          {description && (
            <div className="mt-1 text-[13px] text-[var(--text-secondary)]">{description}</div>
          )}
        </div>
        <div className="max-h-[60vh] overflow-y-auto px-5 py-4">{children}</div>
        {footer && (
          <div className="flex flex-wrap justify-end gap-2 border-t border-[var(--border-subtle)] bg-[var(--surface-sunken)] px-5 py-3.5">
            {footer}
          </div>
        )}
      </div>
    </dialog>
  );
}

/**
 * Right-hand drawer, for inspecting a record without losing the list behind it.
 *
 * On viewports below `sm` it becomes a bottom sheet: a 420px-wide side panel on a phone
 * is just a cramped page (Phase 22 -- don't merely shrink the desktop layout).
 */
export function Drawer({
  open,
  onClose,
  title,
  description,
  children,
  footer,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const opener = useRef<Element | null>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (open && !node.open) {
      opener.current = document.activeElement;
      node.showModal();
    } else if (!open && node.open) {
      node.close();
      if (opener.current instanceof HTMLElement) opener.current.focus();
    }
  }, [open]);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const onCancel = (e: Event) => {
      e.preventDefault();
      onClose();
    };
    node.addEventListener("cancel", onCancel);
    return () => node.removeEventListener("cancel", onCancel);
  }, [onClose]);

  return (
    <dialog
      ref={ref}
      aria-labelledby="drawer-title"
      className={cn(
        "text-[var(--text-primary)] backdrop:bg-black/40",
        // Bottom sheet on small screens...
        "m-0 mt-auto max-h-[85vh] w-full rounded-t-[var(--radius-lg)] p-0",
        // ...side drawer from `sm` up.
        "sm:mt-0 sm:ml-auto sm:h-full sm:max-h-none sm:w-[min(30rem,90vw)] sm:rounded-none sm:rounded-l-[var(--radius-lg)]",
        "border border-[var(--border-default)] bg-[var(--surface-overlay)] shadow-[var(--shadow-lg)]",
        "open:animate-slide-up sm:open:animate-slide-in-right",
      )}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="flex h-full flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-start justify-between gap-3 border-b border-[var(--border-subtle)] px-5 py-4">
          <div className="min-w-0">
            <h2 id="drawer-title" className="text-base font-semibold tracking-tight">
              {title}
            </h2>
            {description && (
              <div className="mt-0.5 text-[13px] text-[var(--text-secondary)]">{description}</div>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="-mr-1 rounded-[var(--radius-sm)] px-2 py-1 text-[var(--text-tertiary)] hover:bg-[var(--surface-sunken)] hover:text-[var(--text-primary)]"
          >
            <span aria-hidden="true">✕</span>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
        {footer && (
          <div className="border-t border-[var(--border-subtle)] bg-[var(--surface-sunken)] px-5 py-3.5">
            {footer}
          </div>
        )}
      </div>
    </dialog>
  );
}
