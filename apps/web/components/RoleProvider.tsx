"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { setApiRole } from "@/lib/api";
import { ROLES, STORAGE_KEY, roleById, type RoleDef } from "@/lib/roles";

const RoleContext = createContext<{
  role: RoleDef;
  setRoleId: (id: string) => void;
}>({ role: ROLES[0], setRoleId: () => undefined });

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [roleId, setRoleId] = useState<string>(ROLES[0].id);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && ROLES.some((r) => r.id === stored)) setRoleId(stored);
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, roleId);
    setApiRole(roleId);
  }, [roleId]);

  const value = useMemo(() => ({ role: roleById(roleId), setRoleId }), [roleId]);
  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>;
}

export function useRole() {
  return useContext(RoleContext);
}
