"use client";

import { useState } from "react";
import type { RunResult } from "@/lib/api";
import { SLA } from "@/lib/sla";
import { AuditEventList } from "./AuditEventList";
import { DecisionRail } from "./DecisionRail";
import { EvidenceDrawer } from "./EvidenceDrawer";
import { FindingGrid } from "./FindingGrid";
import { ProhibitionNotice } from "./ProhibitionNotice";
import { SlaClock } from "./SlaClock";
import { StatusChip } from "./StatusChip";
import { WorkflowBadge } from "./WorkflowBadge";
import type { RoleDef } from "@/lib/roles";

export function CaseFile({
  run,
  role,
  onDecide,
  readOnly = false,
}: {
  run: RunResult;
  role: RoleDef;
  onDecide: Parameters<typeof DecisionRail>[0]["onDecide"];
  readOnly?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [highlight, setHighlight] = useState<string[] | undefined>();
  const payload = run.domain_payload;
  const sla = SLA[run.workflow];

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <div className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <WorkflowBadge workflow={run.workflow} />
              <StatusChip status={run.status} />
              <span className="font-mono text-sm">{run.subject_id}</span>
            </div>
            <div className="mt-1 font-mono text-xs text-muted">
              {run.run_id} · policy {run.policy_contract_version ?? "—"}
            </div>
          </div>
          {run.status === "pending_approval" && (
            <SlaClock deadline={run.hitl_deadline} tier={run.hitl_tier} clock={sla.clock} />
          )}
        </div>

        {run.status === "blocked" && (
          <div className="rounded border border-crimson/40 bg-crimson/10 p-3 text-sm text-crimson">
            Prohibited-action guard blocked this draft. The draft text is not stored. Reason:{" "}
            {run.abstention_reason ?? "prohibited_action"}.
          </div>
        )}

        {run.workflow === "batch_review" && payload?.findings && (
          <section>
            <h2 className="mb-2 text-sm font-semibold text-navy">Reconciliation</h2>
            <FindingGrid findings={payload.findings} onCite={setHighlight} />
          </section>
        )}

        {run.workflow === "pv_intake" && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-navy">PV intake (not a safety determination)</h2>
            <p className="text-xs text-muted">
              Wall-clock SLA — does not pause on weekends. Duplicate candidates are not a merge.
              Terminology suggestions are never auto-applied.
            </p>
            {payload?.candidates && payload.candidates.length > 0 && (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-muted">
                    <th className="py-1">Candidate</th>
                    <th>Similarity</th>
                    <th>Matched fields</th>
                  </tr>
                </thead>
                <tbody>
                  {payload.candidates.map((c) => (
                    <tr key={c.candidate_case_id} className="border-t border-line">
                      <td className="py-1.5 font-mono">{c.candidate_case_id}</td>
                      <td>{c.similarity_score.toFixed(2)}</td>
                      <td>{c.matched_fields.join(", ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {payload?.normalization_suggestions?.map((s) => (
              <div key={s.normalized_term} className="rounded border border-line bg-white px-3 py-2 text-sm">
                {s.normalized_term}{" "}
                <span className="text-muted">
                  ({(s.confidence * 100).toFixed(0)}% · {s.terminology_source} · suggestion only)
                </span>
              </div>
            ))}
          </section>
        )}

        {run.workflow === "supply_planning" && payload?.options && (
          <section>
            <h2 className="mb-2 text-sm font-semibold text-navy">Options (non-executing)</h2>
            <p className="mb-2 text-xs text-muted">No allocate / reserve / ship control exists on this screen.</p>
            <ul className="space-y-2">
              {payload.options.map((o) => (
                <li key={o.option_id} className="rounded border border-line bg-white p-3 text-sm">
                  <div className="font-mono text-xs text-muted">{o.option_id}</div>
                  <p>{o.description}</p>
                  <p className="mt-1 text-xs text-muted">
                    Constraints: {o.constraints_satisfied.join(", ") || "—"}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        )}

        {run.draft_summary && (
          <section>
            <h2 className="mb-1 text-sm font-semibold text-navy">Summary — not a disposition</h2>
            <p className="rounded border border-line bg-white p-3 text-sm">{run.draft_summary}</p>
          </section>
        )}

        {run.draft_claims.length > 0 && (
          <section>
            <h2 className="mb-1 text-sm font-semibold text-navy">Claims</h2>
            <ul className="space-y-1">
              {run.draft_claims.map((c, i) => (
                <li key={i} className="text-sm">
                  {c.text}{" "}
                  {c.cites.map((id) => (
                    <button
                      type="button"
                      key={id}
                      className="ml-1 font-mono text-xs text-batch hover:underline"
                      onClick={() => setHighlight([id])}
                    >
                      [{id}]
                    </button>
                  ))}
                </li>
              ))}
            </ul>
          </section>
        )}

        {(run.critic_reason_codes?.length || run.critic_verdict) && (
          <section>
            <h2 className="mb-1 text-sm font-semibold text-navy">Critic / Verifier</h2>
            <p className="text-sm">
              Verdict: {run.critic_verdict ?? "—"}
              {run.critic_reason_codes?.length
                ? ` · ${run.critic_reason_codes.join(", ")}`
                : ""}
            </p>
          </section>
        )}

        <section>
          <h2 className="mb-2 text-sm font-semibold text-navy">Evidence</h2>
          <EvidenceDrawer items={run.evidence ?? []} highlightIds={highlight} />
        </section>

        <section>
          <h2 className="mb-2 text-sm font-semibold text-navy">Audit</h2>
          <AuditEventList events={run.audit_events ?? []} />
        </section>

        {!readOnly && (
          <DecisionRail
            run={run}
            role={role}
            busy={busy}
            onDecide={async (d) => {
              setBusy(true);
              try {
                await onDecide(d);
              } finally {
                setBusy(false);
              }
            }}
          />
        )}
      </div>
      <div className="space-y-4">
        <ProhibitionNotice workflow={run.workflow} />
        <div className="rounded border border-line bg-white p-3 text-xs text-muted">
          <div className="font-semibold text-navy">Approver roles</div>
          <p className="mt-1">{run.approver_roles.join(", ") || "—"}</p>
          <p className="mt-2">Requested by {run.requester_role}</p>
        </div>
      </div>
    </div>
  );
}
