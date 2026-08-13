"use client";

import { AppShell } from "@/components/AppShell";
import { InboxList } from "@/components/InboxList";
import { SubmitForm } from "@/components/SubmitForm";
import { getQueue, type QueueEntry } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";

export default function SupplyWorkspace() {
  const [entries, setEntries] = useState<QueueEntry[]>([]);
  const refresh = useCallback(async () => {
    try {
      setEntries(await getQueue("supply_planning"));
    } catch {
      setEntries([]);
    }
  }, []);
  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  return (
    <AppShell title="Supply Planning">
      <p className="mb-6 max-w-2xl text-sm text-muted">
        Ranked, non-executing options. Dual approval: Supply Chain VP (planning) and EU Qualified
        Person (quality). Partial approval is not approval. No allocate control exists.
      </p>
      <SubmitForm defaultWorkflow="supply_planning" lockWorkflow />
      <h2 className="mb-2 mt-8 text-sm font-semibold text-navy">Pending</h2>
      <InboxList entries={entries} filter="supply_planning" onFilter={() => undefined} hideFilters />
    </AppShell>
  );
}
