"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { useAuth } from "./AuthContext";

/**
 * The signed-in identity control in the sidebar footer. Replaced the old "claimed
 * identity" free-text picker (Phase 25's honest "no sign-in" warning) once Stage 22 added
 * real login -- what's shown here is the authenticated session from
 * services/api/auth.py, not a self-reported label.
 */
export function OperatorBar() {
  const { session, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [signingOut, setSigningOut] = useState(false);

  if (!session) return null;

  async function handleSignOut() {
    setSigningOut(true);
    try {
      await signOut();
    } finally {
      setSigningOut(false);
      setOpen(false);
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex w-full items-center gap-2.5 rounded-[var(--radius-md)] px-2 py-2 text-left hover:bg-[var(--surface-sunken)]"
      >
        <span
          aria-hidden="true"
          className="grid size-7 shrink-0 place-items-center rounded-full border border-[var(--border-default)] bg-[var(--surface-sunken)] text-[11px] font-semibold text-[var(--text-secondary)]"
        >
          {initials(session.display_name)}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-[12px] font-medium text-[var(--text-primary)]">
            {session.display_name}
          </span>
          <span className="block truncate text-[10px] text-[var(--text-tertiary)]">
            {session.role}
          </span>
        </span>
      </button>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title="Signed in"
        description="Attached to every action you take as the authenticated approver of record."
        footer={
          <Button variant="danger" onClick={handleSignOut} loading={signingOut} loadingLabel="Signing out…">
            Sign out
          </Button>
        }
      >
        <dl className="space-y-2.5 text-[13px]">
          <div className="flex justify-between gap-3">
            <dt className="text-[var(--text-tertiary)]">Name</dt>
            <dd className="font-medium text-[var(--text-primary)]">{session.display_name}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-[var(--text-tertiary)]">User ID</dt>
            <dd className="font-mono text-[var(--text-primary)]">{session.user_id}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-[var(--text-tertiary)]">Role</dt>
            <dd className="font-medium text-[var(--text-primary)]">{session.role}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-[var(--text-tertiary)]">Session expires</dt>
            <dd className="text-[var(--text-primary)]">
              {new Date(session.expires_at).toLocaleString()}
            </dd>
          </div>
        </dl>
      </Dialog>
    </>
  );
}

function initials(value: string): string {
  const cleaned = value.replace(/[^a-zA-Z ]/g, " ").trim();
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
