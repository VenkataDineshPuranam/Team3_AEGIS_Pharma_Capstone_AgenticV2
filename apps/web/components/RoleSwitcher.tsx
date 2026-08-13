"use client";

import { ROLES } from "@/lib/roles";
import { useRole } from "./RoleProvider";

export function RoleSwitcher() {
  const { role, setRoleId } = useRole();
  return (
    <label className="block text-xs text-white/70">
      Acting as (Entra stub)
      <select
        className="mt-1 w-full rounded border border-white/20 bg-navy-2 px-2 py-1.5 text-sm text-white"
        value={role.id}
        onChange={(e) => setRoleId(e.target.value)}
      >
        {ROLES.map((r) => (
          <option key={r.id} value={r.id}>
            {r.label}
            {r.requesterOnly ? " — requester only" : ""}
          </option>
        ))}
      </select>
    </label>
  );
}
