"use client";

import { AppShell } from "@/components/AppShell";
import { InboxList } from "@/components/InboxList";
import { SubmitForm } from "@/components/SubmitForm";
import { getQueue, type QueueEntry } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";

export default function PvWorkspace() {
  const [entries, setEntries] = useState<QueueEntry[]>([]);
  const refresh = useCallback(async () => {
    try {
      setEntries(await getQueue("pv_intake"));
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
    <AppShell title="PV Intake">
      <p className="mb-6 max-w-2xl text-sm text-muted">
        Duplicate candidates, terminology suggestions, and clock reconstruction. 100% human review.
        Causality, seriousness, expectedness and reportability are structurally absent. Wall-clock SLA.
      </p>
      <SubmitForm defaultWorkflow="pv_intake" lockWorkflow />
      <h2 className="mb-2 mt-8 text-sm font-semibold text-navy">Pending</h2>
      <InboxList entries={entries} filter="pv_intake" onFilter={() => undefined} hideFilters />
    </AppShell>
  );
}
