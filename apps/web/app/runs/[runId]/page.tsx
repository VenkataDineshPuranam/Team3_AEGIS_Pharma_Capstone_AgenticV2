"use client";

import { use } from "react";
import { RunDetailView } from "@/components/decisions/RunDetailView";

/**
 * A historical run, opened from Run History. Same investigation-quality workspace as the
 * live decision detail (Phase 17) — evidence, governance, and the full audit timeline are
 * identical regardless of whether the run is still pending or was decided last week.
 */
export default function RunHistoryDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = use(params);
  return (
    <RunDetailView
      runId={runId}
      backHref="/runs"
      backLabel="Run History"
      afterDecideHref="/runs"
    />
  );
}
