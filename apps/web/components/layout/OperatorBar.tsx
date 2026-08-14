"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { Select } from "@/components/ui/Form";
import { Notice } from "@/components/ui/States";
import { DOMAIN_ROLES, useOperator, type DomainRole } from "./OperatorContext";

/**
 * The operator identity control in the sidebar footer.
 *
 * Every surface of this control says the same thing: this is not a login. The warning is
 * not tucked into a tooltip, because a user who believes they are authenticated when they
 * are not is exactly the misunderstanding this build must not create (Phase 25).
 */
export function OperatorBar() {
  const { role, identity } = useOperator();
  const [open, setOpen] = useState(false);

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
          {initials(identity || role)}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-[12px] font-medium text-[var(--text-primary)]">
            {role}
          </span>
          <span className="flex items-center gap-1 text-[10px] text-[var(--status-pending-fg)]">
            <span aria-hidden="true">!</span> Unverified — no sign-in
          </span>
        </span>
      </button>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title="Operator context"
        description="Used to label your actions in the audit trail. It is not a sign-in."
        footer={
          <Button variant="primary" onClick={() => setOpen(false)}>
            Done
          </Button>
        }
      >
        <div className="space-y-4">
          <Notice tone="warning" title="This application has no authentication">
            Nothing you select here grants any permission. The Orchestrator API performs no
            server-side authorization in this build: anyone who can reach it can submit a run
            and record a decision, with any role string. Your selection is recorded alongside
            your decisions as a <strong>claimed, unverified</strong> label, so the audit trail
            reflects what was asserted rather than what was proven.
            <br />
            <br />
            Microsoft Entra ID is the planned identity provider. Until it is in place, this
            application should not be deployed outside a trusted local environment.
          </Notice>

          <RoleSelect />
          <IdentityInput />
        </div>
      </Dialog>
    </>
  );
}

function RoleSelect() {
  const { role, setRole } = useOperator();
  return (
    <Select
      label="Acting as"
      value={role}
      onChange={(e) => setRole(e.target.value as DomainRole)}
      hint="Determines which queues are highlighted for you. It does not gate any action."
    >
      {DOMAIN_ROLES.map((r) => (
        <option key={r} value={r}>
          {r}
        </option>
      ))}
    </Select>
  );
}

function IdentityInput() {
  const { identity, setIdentity } = useOperator();
  return (
    <div>
      <label
        htmlFor="operator-identity"
        className="block text-[13px] font-medium text-[var(--text-primary)]"
      >
        Identifier <span className="font-normal text-[var(--text-tertiary)]">(optional)</span>
      </label>
      <p className="mt-1 text-xs text-[var(--text-tertiary)]">
        Recorded with your decisions as unverified context — for example a name or work email.
      </p>
      <input
        id="operator-identity"
        type="text"
        value={identity}
        maxLength={200}
        onChange={(e) => setIdentity(e.target.value)}
        placeholder="e.g. a.qp@novacura.example"
        className="mt-1.5 w-full rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-raised)] px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]"
      />
    </div>
  );
}

function initials(value: string): string {
  const cleaned = value.replace(/[^a-zA-Z ]/g, " ").trim();
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
