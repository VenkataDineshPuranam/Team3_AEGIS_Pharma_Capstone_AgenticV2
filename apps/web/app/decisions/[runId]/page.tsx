"use client";

import { use } from "react";
import { RunDetailView } from "@/components/decisions/RunDetailView";

/**
 * A decision opened from the queue. Same workspace as a historical run — the only
 * difference is where "back" goes, because an approver arriving here is mid-task and
 * should land back in the queue they were working.
 */
export default function DecisionDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = use(params);
  return <RunDetailView runId={runId} backHref="/decisions" backLabel="Decision Queue" />;
}
