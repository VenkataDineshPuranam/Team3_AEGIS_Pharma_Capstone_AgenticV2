"use client";

import { useState } from "react";
import type { EvidenceItem } from "@/lib/api";

export function EvidenceDrawer({
  items,
  highlightIds,
}: {
  items: EvidenceItem[];
  highlightIds?: string[];
}) {
  const [openId, setOpenId] = useState<string | null>(highlightIds?.[0] ?? null);
  if (!items.length) {
    return <p className="text-sm text-muted">No citable evidence in this run.</p>;
  }
  return (
    <ul className="divide-y divide-line rounded border border-line bg-white">
      {items.map((e) => {
        const hot = highlightIds?.includes(e.evidence_id);
        const open = openId === e.evidence_id;
        return (
          <li key={e.evidence_id} className={hot ? "bg-amber/5" : ""}>
            <button
              type="button"
              className="flex w-full items-start justify-between gap-3 px-3 py-2 text-left"
              onClick={() => setOpenId(open ? null : e.evidence_id)}
            >
              <div>
                <div className="font-mono text-xs text-navy">{e.evidence_id}</div>
                <div className="text-sm">{e.source}</div>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span
                  className={
                    e.status === "draft"
                      ? "rounded bg-amber/15 px-1.5 py-0.5 text-amber"
                      : "rounded bg-emerald/10 px-1.5 py-0.5 text-emerald"
                  }
                >
                  {e.status}
                </span>
                {e.jurisdiction && (
                  <span className="text-muted" title="Citable only within this jurisdiction">
                    {e.jurisdiction}
                  </span>
                )}
              </div>
            </button>
            {open && (
              <div className="border-t border-line px-3 py-2 text-sm text-muted">
                <div>Effective {e.effective_date ?? "—"}</div>
                {e.content_excerpt && <p className="mt-2 text-ink">{e.content_excerpt}</p>}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
