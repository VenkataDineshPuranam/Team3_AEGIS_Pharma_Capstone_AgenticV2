"use client";

import { Badge } from "@/components/ui/Badge";
import { Notice } from "@/components/ui/States";
import { RunEvidenceCard } from "@/components/evidence/EvidenceCard";
import type { QueueEntry } from "@/lib/api";
import { WORKFLOW_BOUNDARY } from "@/lib/format";

/**
 * The decision-support package, presented for reading rather than parsing (Phase 8).
 *
 * Sections follow the order a reviewer actually needs them: what the system concluded,
 * what is missing, then what each conclusion rests on. Claims are grouped by whether they
 * carry a citation, because an uncited claim is the single most important thing for a
 * reviewer to notice and is easy to miss in a flat list.
 */
export function DecisionSupport({ entry }: { entry: QueueEntry }) {
  const boundary = WORKFLOW_BOUNDARY[entry.workflow];
  const cited = entry.draft_claims.filter((c) => c.cites.length > 0);
  const uncited = entry.draft_claims.filter((c) => c.cites.length === 0);

  // Which evidence item supports which claim -- the Finding → Evidence half of the
  // traceability chain (Phase 10), built from the run's own data, not inferred.
  const claimsByEvidence = new Map<string, string[]>();
  for (const claim of entry.draft_claims) {
    for (const id of claim.cites) {
      claimsByEvidence.set(id, [...(claimsByEvidence.get(id) ?? []), claim.text]);
    }
  }
  const orphanCitations = [...claimsByEvidence.keys()].filter(
    (id) => !entry.evidence.some((e) => e.evidence_id === id),
  );

  return (
    <div className="space-y-6">
      {/* --- summary --------------------------------------------------- */}
      <section aria-labelledby="ds-summary">
        <h3
          id="ds-summary"
          className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]"
        >
          Summary
        </h3>
        {entry.draft_summary ? (
          <p className="mt-2 text-[14px] leading-relaxed text-[var(--text-primary)]">
            {entry.draft_summary}
          </p>
        ) : (
          <p className="mt-2 text-[13px] italic text-[var(--text-tertiary)]">
            No summary was produced. The run reached its interrupt without a synthesized
            output.
          </p>
        )}
      </section>

      {/* --- findings -------------------------------------------------- */}
      {cited.length > 0 && (
        <section aria-labelledby="ds-findings">
          <h3
            id="ds-findings"
            className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]"
          >
            Key findings
            <span className="ml-2 font-normal normal-case tracking-normal text-[var(--text-tertiary)]">
              each traced to the evidence it cites
            </span>
          </h3>
          <ul className="mt-2 space-y-2">
            {cited.map((claim, i) => (
              <li
                key={i}
                className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] px-3.5 py-3"
              >
                <p className="text-[13px] leading-relaxed text-[var(--text-primary)]">
                  {claim.text}
                </p>
                <p className="mt-1.5 flex flex-wrap items-center gap-1.5">
                  <span className="text-[10px] uppercase tracking-wider text-[var(--text-tertiary)]">
                    Cites
                  </span>
                  {claim.cites.map((id) => (
                    <span
                      key={id}
                      className="rounded-[var(--radius-sm)] bg-[var(--surface-sunken)] px-1.5 py-0.5 font-mono text-[11px] text-[var(--text-secondary)]"
                    >
                      {id}
                    </span>
                  ))}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* --- exceptions ------------------------------------------------ */}
      {(uncited.length > 0 || orphanCitations.length > 0) && (
        <section aria-labelledby="ds-exceptions">
          <h3
            id="ds-exceptions"
            className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]"
          >
            Exceptions and gaps
          </h3>

          {uncited.length > 0 && (
            <Notice
              tone="warning"
              className="mt-2"
              title={`${uncited.length} statement${uncited.length === 1 ? "" : "s"} carry no citation`}
            >
              <ul className="mt-1.5 space-y-1">
                {uncited.map((claim, i) => (
                  <li key={i} className="text-[13px] text-[var(--text-primary)]">
                    {claim.text}
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-[12px]">
                An uncited statement is not supported by retrieved evidence. Weigh it
                accordingly, or reject and require a citation.
              </p>
            </Notice>
          )}

          {orphanCitations.length > 0 && (
            <Notice
              tone="blocked"
              className="mt-2"
              title="A citation does not resolve to this run's evidence"
            >
              <span className="font-mono">{orphanCitations.join(", ")}</span> — cited by a
              finding but absent from the evidence this run retrieved. Treat the finding as
              unsupported.
            </Notice>
          )}
        </section>
      )}

      {/* --- evidence -------------------------------------------------- */}
      <section aria-labelledby="ds-evidence">
        <h3
          id="ds-evidence"
          className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]"
        >
          Evidence
          <Badge tone="authoritative" size="xs">
            {entry.evidence.length} retrieved
          </Badge>
        </h3>
        <p className="mt-1.5 text-[12px] leading-relaxed text-[var(--text-tertiary)]">
          Every item below passed the authority filter inside the retrieval tool before this
          run could see it. Untrusted and superseded documents are excluded server-side and
          never reach a run — there is no code path that would return one here.
        </p>

        {entry.evidence.length === 0 ? (
          <p className="mt-2 text-[13px] italic text-[var(--text-tertiary)]">
            No evidence is attached to this run.
          </p>
        ) : (
          <ul className="mt-2.5 space-y-2">
            {entry.evidence.map((item) => (
              <li key={item.evidence_id}>
                <RunEvidenceCard
                  item={item}
                  citedBy={claimsByEvidence.get(item.evidence_id)}
                />
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* --- the boundary, restated where the decision is made --------- */}
      <section aria-labelledby="ds-boundary">
        <h3
          id="ds-boundary"
          className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]"
        >
          What this analysis does not conclude
        </h3>
        <ul className="mt-2 space-y-1.5">
          {boundary.neverDoes.map((item) => (
            <li
              key={item}
              className="flex items-start gap-2 text-[13px] text-[var(--text-secondary)]"
            >
              <span
                aria-hidden="true"
                className="mt-0.5 shrink-0 text-[var(--status-blocked-fg)]"
              >
                ⊘
              </span>
              {item}
            </li>
          ))}
        </ul>
        <p className="mt-2 text-[12px] leading-relaxed text-[var(--text-tertiary)]">
          These are not stylistic restraints. The output schema has no field that could
          express them, no tool exposes the capability, and a runtime guard checks the
          generated text against a versioned prohibition list — twice.
        </p>
      </section>
    </div>
  );
}
