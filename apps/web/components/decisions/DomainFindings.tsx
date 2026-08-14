"use client";

import { Badge } from "@/components/ui/Badge";
import { Notice } from "@/components/ui/States";
import { cn } from "@/lib/cn";
import type {
  BatchPayload,
  ClinicalPayload,
  DomainPayload,
  PVPayload,
  RegulatoryPayload,
  ResearchPayload,
  SupplyPayload,
  Workflow,
} from "@/lib/api";
import { humanize } from "@/lib/format";

/**
 * Structured findings, rendered per workflow.
 *
 * Phase 8: never dump raw JSON on the user. Phase 11: do not force all three workflows
 * into one UI — a batch reconciliation matrix, a duplicate-candidate list, and a set of
 * planning options are genuinely different objects, and flattening them into a generic
 * key/value table would lose the meaning that makes each one useful.
 *
 * Each renderer below is faithful to its payload type in packages/domain/payloads.py.
 * None of them invents a field, and none of them derives a disposition: these models
 * structurally cannot express one, and the UI must not add one on top.
 */
export function DomainFindings({
  workflow,
  payload,
}: {
  workflow: Workflow;
  payload: DomainPayload | null;
}) {
  if (!payload) {
    return (
      <p className="text-[13px] text-[var(--text-tertiary)] italic">
        No structured findings were produced — the run ended before its domain tool ran.
      </p>
    );
  }
  if (workflow === "batch_review") {
    return (
      <ReconciliationFindings
        payload={payload as BatchPayload}
        noticeBody="These are structural completeness and conflict findings only. AEGIS does not assess whether this batch is fit for release, and holds no field that could express it. Certification is the Qualified Person's decision alone."
      />
    );
  }
  if (workflow === "pv_intake") return <PVFindings payload={payload as PVPayload} />;
  if (workflow === "supply_planning") return <SupplyFindings payload={payload as SupplyPayload} />;
  if (workflow === "research_review") {
    return (
      <ReconciliationFindings
        payload={payload as ResearchPayload}
        noticeBody="These are structural completeness and conflict findings only. AEGIS does not assess whether a model is qualified or a target is validated, and holds no field that could express it. That determination is the Research/Portfolio reviewer's alone."
      />
    );
  }
  if (workflow === "clinical_integrity") {
    return (
      <ReconciliationFindings
        payload={payload as ClinicalPayload}
        noticeBody="These are structural completeness and conflict findings only. AEGIS does not determine eligibility, take an unblinding action, or dispose of a protocol deviation, and holds no field that could express any of those. Those are the clinical/medical monitor's decisions alone."
      />
    );
  }
  return (
    <ReconciliationFindings
      payload={payload as RegulatoryPayload}
      noticeBody="These are structural completeness and conflict findings only. AEGIS does not classify a variation or determine submission readiness, and holds no field that could express either. Those are Regulatory Affairs' decisions alone."
    />
  );
}

/* ------------------------------------------------------- reconciliation --- */
/* Shared by batch_review, research_review, clinical_integrity and
   regulatory_completeness -- all four payloads share the exact
   (reconciliation_complete, findings[category/status/evidence_ids/gap_description])
   shape (packages/domain/payloads.py), so one renderer serves all four faithfully. */

const FINDING_STATUS_TONE = {
  complete: "ok",
  gap: "pending",
  conflict: "blocked",
} as const;

function ReconciliationFindings({
  payload,
  noticeBody,
}: {
  payload: { reconciliation_complete: boolean; findings: BatchPayload["findings"] };
  noticeBody: string;
}) {
  const gaps = payload.findings.filter((f) => f.status !== "complete");

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={payload.reconciliation_complete ? "ok" : "pending"}>
          {payload.reconciliation_complete
            ? "Reconciliation complete"
            : "Reconciliation incomplete"}
        </Badge>
        <span className="text-[13px] text-[var(--text-secondary)]">
          {payload.findings.length} categories assessed
          {gaps.length > 0 && (
            <>
              , <span className="font-medium text-[var(--status-pending-fg)]">{gaps.length}</span>{" "}
              with gaps or conflicts
            </>
          )}
        </span>
      </div>

      <ul className="grid gap-2 sm:grid-cols-2">
        {payload.findings.map((finding) => (
          <li
            key={finding.category}
            className={cn(
              "rounded-[var(--radius-md)] border px-3 py-2.5",
              finding.status === "complete"
                ? "border-[var(--border-subtle)] bg-[var(--surface-raised)]"
                : "border-[var(--status-pending-border)] bg-[var(--status-pending-bg)]",
            )}
          >
            <div className="flex items-start justify-between gap-2">
              <span className="text-[13px] font-medium text-[var(--text-primary)]">
                {humanize(finding.category)}
              </span>
              <Badge tone={FINDING_STATUS_TONE[finding.status]} size="xs">
                {humanize(finding.status)}
              </Badge>
            </div>
            {finding.gap_description && (
              <p className="mt-1.5 text-[12px] leading-relaxed text-[var(--text-secondary)]">
                {finding.gap_description}
              </p>
            )}
            {finding.evidence_ids.length > 0 && (
              <p className="mt-1.5 font-mono text-[11px] text-[var(--text-tertiary)]">
                {finding.evidence_ids.join(", ")}
              </p>
            )}
          </li>
        ))}
      </ul>

      <Notice tone="info" title="What this does not say">
        {noticeBody}
      </Notice>
    </div>
  );
}

/* ------------------------------------------------------------------- pv --- */

function PVFindings({ payload }: { payload: PVPayload }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={payload.duplicate_suspected ? "pending" : "ok"}>
          {payload.duplicate_suspected
            ? "Duplicate suspected"
            : "No duplicate suspected"}
        </Badge>
        <span className="text-[12px] text-[var(--text-tertiary)]">
          Comparison window {payload.comparison_window_version}
        </span>
      </div>

      <section>
        <h4 className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
          Duplicate candidates
        </h4>
        {payload.candidates.length === 0 ? (
          <p className="mt-1.5 text-[13px] text-[var(--text-secondary)]">
            No candidate cases matched within the comparison window.
          </p>
        ) : (
          <ul className="mt-2 space-y-2">
            {payload.candidates.map((candidate) => (
              <li
                key={candidate.candidate_case_id}
                className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] px-3 py-2.5"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-[13px] font-medium text-[var(--text-primary)]">
                    {candidate.candidate_case_id}
                  </span>
                  <span className="tnum text-[12px] text-[var(--text-secondary)]">
                    similarity {candidate.similarity_score.toFixed(2)}
                  </span>
                </div>
                {/* A similarity bar, not a verdict: the score is structural evidence for a
                    human triage decision, never a duplicate determination. */}
                <div className="mt-2 h-1 overflow-hidden rounded-full bg-[var(--surface-sunken)]">
                  <div
                    className="h-full bg-[var(--status-pending-fg)]"
                    style={{ width: `${Math.min(100, candidate.similarity_score * 100)}%` }}
                  />
                </div>
                <p className="mt-1.5 text-[11px] text-[var(--text-tertiary)]">
                  Matched on: {candidate.matched_fields.map(humanize).join(", ")}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
          Terminology normalization{" "}
          <span className="font-normal normal-case tracking-normal">
            (suggestions — never applied)
          </span>
        </h4>
        {payload.normalization_suggestions.length === 0 ? (
          <p className="mt-1.5 text-[13px] text-[var(--text-secondary)]">
            No normalization suggestions were produced.
          </p>
        ) : (
          <ul className="mt-2 space-y-1.5">
            {payload.normalization_suggestions.map((s, i) => (
              <li
                key={i}
                className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded-[var(--radius-md)] border border-[var(--border-subtle)] px-3 py-2 text-[13px]"
              >
                <span className="font-medium text-[var(--text-primary)]">{s.normalized_term}</span>
                <span className="tnum text-[12px] text-[var(--text-tertiary)]">
                  confidence {s.confidence.toFixed(2)}
                </span>
                <span className="ml-auto text-[11px] text-[var(--text-tertiary)]">
                  {s.terminology_source}
                </span>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-[11px] text-[var(--text-tertiary)]">
          Terminology table {payload.terminology_table_version}. Suggestions are never applied
          automatically — the schema has no field that could record one as applied.
        </p>
      </section>

      <Notice tone="info" title="What this does not say">
        AEGIS produces intake and triage support only. It does not determine seriousness,
        causality, expectedness or reportability, and does not confirm a signal. Those
        determinations belong to the Global Head of Pharmacovigilance.
      </Notice>
    </div>
  );
}

/* --------------------------------------------------------------- supply --- */

function SupplyFindings({ payload }: { payload: SupplyPayload }) {
  const constraints = Object.entries(payload.constraint_set).filter(([, v]) =>
    Array.isArray(v) ? v.length > 0 : Boolean(v),
  );

  return (
    <div className="space-y-4">
      {/* The distinction Phase 11 requires, stated before the options are read. */}
      <Notice tone="warning" title="These are planning options, not executable actions">
        Each option below is a proposal for a human planner to evaluate. Nothing here
        allocates or reserves inventory, authorizes a shipment, or initiates a recall —
        AEGIS holds no capability to do any of those, and this interface exposes no control
        that would.
      </Notice>

      <div className="flex flex-wrap items-center gap-2 text-[12px] text-[var(--text-tertiary)]">
        <span>
          <span className="tnum font-medium text-[var(--text-primary)]">
            {payload.options.length}
          </span>{" "}
          option{payload.options.length === 1 ? "" : "s"} generated
        </span>
        <span aria-hidden="true">·</span>
        <span>Inventory snapshot {payload.inventory_snapshot_version}</span>
      </div>

      <ul className="space-y-2.5">
        {payload.options.map((option, index) => (
          <li
            key={option.option_id}
            className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] px-3.5 py-3"
          >
            <div className="flex flex-wrap items-center gap-2">
              <span
                aria-hidden="true"
                className="grid size-5 shrink-0 place-items-center rounded-[var(--radius-sm)] bg-[var(--surface-sunken)] text-[11px] font-semibold text-[var(--text-secondary)]"
              >
                {index + 1}
              </span>
              <span className="font-mono text-[13px] font-medium text-[var(--text-primary)]">
                {option.option_id}
              </span>
              <Badge tone="neutral" size="xs">
                PLANNING OPTION
              </Badge>
            </div>

            <p className="mt-2 text-[13px] leading-relaxed text-[var(--text-primary)]">
              {option.description}
            </p>

            {option.transport_notes && (
              <p className="mt-2 rounded-[var(--radius-sm)] bg-[var(--surface-sunken)] px-2.5 py-1.5 text-[12px] text-[var(--text-secondary)]">
                <span className="font-medium">Transport & cold chain:</span>{" "}
                {option.transport_notes}
              </p>
            )}

            <div className="mt-2.5 flex flex-wrap gap-x-4 gap-y-1.5 text-[11px]">
              {option.constraints_satisfied.length > 0 && (
                <p className="text-[var(--text-tertiary)]">
                  <span className="font-medium text-[var(--status-ok-fg)]">✓ Satisfies:</span>{" "}
                  {option.constraints_satisfied.map(humanize).join(", ")}
                </p>
              )}
              {option.cold_chain_evidence_ids.length > 0 && (
                <p className="font-mono text-[var(--text-tertiary)]">
                  Cold-chain evidence: {option.cold_chain_evidence_ids.join(", ")}
                </p>
              )}
            </div>
          </li>
        ))}
      </ul>

      {constraints.length > 0 && (
        <section>
          <h4 className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
            Constraint set
          </h4>
          <dl className="mt-2 grid gap-2 sm:grid-cols-2">
            {constraints.map(([key, value]) => (
              <div key={key} className="rounded-[var(--radius-md)] bg-[var(--surface-sunken)] px-3 py-2">
                <dt className="text-[11px] text-[var(--text-tertiary)]">{humanize(key)}</dt>
                <dd className="mt-0.5 text-[12px] text-[var(--text-primary)]">
                  {Array.isArray(value) ? value.join(", ") : String(value)}
                </dd>
              </div>
            ))}
          </dl>
          <p className="mt-2 text-[11px] text-[var(--text-tertiary)]">
            The agent may rank and explain within this constraint-filtered set. It cannot
            widen it.
          </p>
        </section>
      )}
    </div>
  );
}
