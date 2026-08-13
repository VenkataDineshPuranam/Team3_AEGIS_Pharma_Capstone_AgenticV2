"use client";

import { AppShell } from "@/components/AppShell";
import { SubmitForm } from "@/components/SubmitForm";
import { InboxList } from "@/components/InboxList";
import { getQueue, type QueueEntry, type Workflow } from "@/lib/api";
import { useCallback, useEffect, useState } from "react";

function Workspace({
  workflow,
  title,
  intro,
}: {
  workflow: Workflow;
  title: string;
  intro: string;
}) {
  const [entries, setEntries] = useState<QueueEntry[]>([]);

  const refresh = useCallback(async () => {
    try {
      setEntries(await getQueue(workflow));
    } catch {
      setEntries([]);
    }
  }, [workflow]);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, [refresh]);

  return (
    <AppShell title={title}>
      <p className="mb-6 max-w-2xl text-sm text-muted">{intro}</p>
      <h2 className="mb-2 text-sm font-semibold text-navy">Submit</h2>
      <SubmitForm defaultWorkflow={workflow} lockWorkflow />
      <h2 className="mb-2 mt-8 text-sm font-semibold text-navy">Pending in this workflow</h2>
      <InboxList entries={entries} filter={workflow} onFilter={() => undefined} hideFilters />
    </AppShell>
  );
}

export default function BatchWorkspace() {
  return (
    <Workspace
      workflow="batch_review"
      title="Batch Review"
      intro="Reconcile genealogy, lab, deviations, CAPA and packet completeness. The EU Qualified Person reviews the pack. The system never certifies a batch. Manufacturing VP is never an approver."
    />
  );
}
