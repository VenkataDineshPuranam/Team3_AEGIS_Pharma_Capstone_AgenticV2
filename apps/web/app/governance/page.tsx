"use client";

import { PageBody, PageHeader } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { ErrorState, Notice, SkeletonText } from "@/components/ui/States";
import { useApiResource } from "@/hooks/useApiResource";
import { getGovernance } from "@/lib/api";
import { WORKFLOW_LABELS, humanize } from "@/lib/format";

/**
 * Governance Center.
 *
 * Every value on this page is read from the artefact that actually enforces it — the
 * policy contract file, the graph modules' own constants, the retrieval tool's citable
 * set (see services/api/governance_view.py). Nothing here is a second, hand-maintained
 * copy of a rule that could drift from what is actually enforced.
 */
export default function GovernancePage() {
  const gov = useApiResource((s) => getGovernance(s), []);

  return (
    <>
      <PageHeader
        title="Governance"
        description="The controls that make AEGIS more than a language model with a chat window: deterministic policy, evidence authority, and human accountability, read directly from what enforces them."
        actions={
          <Button variant="secondary" onClick={gov.refresh} loading={gov.loading}>
            Refresh
          </Button>
        }
      />

      <PageBody className="space-y-6">
        {gov.error ? (
          <ErrorState message={gov.error.userMessage} action={<Button onClick={gov.refresh}>Try again</Button>} />
        ) : !gov.data ? (
          <Card>
            <CardBody>
              <SkeletonText lines={10} />
            </CardBody>
          </Card>
        ) : (
          <>
            {/* --- authentication, first and unambiguous ---------------- */}
            <Notice tone="warning" title={`Authentication: ${gov.data.authentication.status}`}>
              {gov.data.authentication.detail}
              <br />
              <br />
              <strong>Planned:</strong> {gov.data.authentication.planned}
            </Notice>

            {/* --- prohibited actions ------------------------------------ */}
            <Card>
              <CardHeader
                title="Prohibited actions"
                description={`Policy contract ${gov.data.policy_contract_version} — ${gov.data.prohibited_actions.status}`}
              />
              <CardBody className="space-y-5">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
                    Three independent enforcement layers
                  </p>
                  <ol className="mt-2 space-y-2">
                    {gov.data.prohibited_actions.enforcement.map((line, i) => (
                      <li key={i} className="flex gap-2.5 text-[13px] leading-relaxed text-[var(--text-secondary)]">
                        <span className="mt-0.5 shrink-0 font-mono text-[11px] text-[var(--text-tertiary)]">
                          {i + 1}
                        </span>
                        {line}
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="grid gap-4 lg:grid-cols-3">
                  {Object.entries(gov.data.prohibited_actions.by_workflow).map(([wf, contract]) => (
                    <div
                      key={wf}
                      className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] p-3.5"
                    >
                      <p className="text-[13px] font-semibold text-[var(--text-primary)]">
                        {WORKFLOW_LABELS[wf as keyof typeof WORKFLOW_LABELS] ?? humanize(wf)}
                      </p>
                      <p className="mt-2 text-[11px] font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
                        Banned terms ({contract.banned_terms.length})
                      </p>
                      <ul className="mt-1 flex flex-wrap gap-1">
                        {contract.banned_terms.slice(0, 6).map((term) => (
                          <li
                            key={term}
                            className="rounded-[var(--radius-sm)] bg-[var(--status-blocked-bg)] px-1.5 py-0.5 text-[11px] text-[var(--status-blocked-fg)]"
                          >
                            “{term}”
                          </li>
                        ))}
                        {contract.banned_terms.length > 6 && (
                          <li className="text-[11px] text-[var(--text-tertiary)]">
                            +{contract.banned_terms.length - 6} more
                          </li>
                        )}
                      </ul>
                      <p className="mt-2 text-[11px] font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
                        Banned fields
                      </p>
                      <p className="mt-1 font-mono text-[11px] text-[var(--text-secondary)]">
                        {contract.banned_field_names.join(", ")}
                      </p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* --- approver roles ----------------------------------------- */}
            <Card>
              <CardHeader
                title="Approver roles and structure"
                description="Who is accountable for each workflow's terminal decision"
              />
              <CardBody className="grid gap-4 lg:grid-cols-3">
                {Object.entries(gov.data.approver_roles).map(([wf, role]) => (
                  <div
                    key={wf}
                    className="rounded-[var(--radius-md)] border border-[var(--border-subtle)] p-3.5"
                  >
                    <p className="text-[13px] font-semibold text-[var(--text-primary)]">
                      {WORKFLOW_LABELS[wf as keyof typeof WORKFLOW_LABELS] ?? humanize(wf)}
                    </p>
                    <p className="mt-1.5 text-[12px] text-[var(--text-secondary)]">
                      {role.primary.join(", ")}
                    </p>
                    {role.escalation && (
                      <p className="mt-1 text-[11px] text-[var(--text-tertiary)]">
                        Escalates to: {role.escalation}
                      </p>
                    )}
                    {role.veto_role && (
                      <Badge tone="blocked" size="xs" className="mt-2">
                        Veto: {role.veto_role}
                      </Badge>
                    )}
                    {role.required_legs && (
                      <Badge tone="pending" size="xs" className="mt-2">
                        Dual approval — both legs required
                      </Badge>
                    )}
                    <p className="mt-2 text-[11px] leading-relaxed text-[var(--text-tertiary)]">
                      {role.structure}
                    </p>
                  </div>
                ))}
              </CardBody>
            </Card>

            {/* --- HITL rules --------------------------------------------- */}
            <Card>
              <CardHeader title="Human-in-the-loop rules" description={gov.data.hitl_rules.source} />
              <CardBody className="space-y-4">
                <div className="flex flex-wrap gap-3">
                  {Object.entries(gov.data.hitl_rules.escalation_ladder_hours).map(([tier, hours]) => (
                    <div
                      key={tier}
                      className="rounded-[var(--radius-md)] bg-[var(--surface-sunken)] px-3 py-2 text-center"
                    >
                      <p className="tnum text-lg font-semibold text-[var(--text-primary)]">{hours}h</p>
                      <p className="text-[10px] uppercase tracking-wider text-[var(--text-tertiary)]">
                        {humanize(tier)}
                      </p>
                    </div>
                  ))}
                </div>
                <ul className="space-y-1.5">
                  {gov.data.hitl_rules.invariants.map((rule, i) => (
                    <li key={i} className="flex gap-2 text-[13px] text-[var(--text-secondary)]">
                      <span aria-hidden="true" className="mt-0.5 shrink-0 text-[var(--status-ok-fg)]">
                        ✓
                      </span>
                      {rule}
                    </li>
                  ))}
                </ul>
                <Notice tone="warning" title="Escalation clock status">
                  {gov.data.hitl_rules.clock_status}
                </Notice>
              </CardBody>
            </Card>

            {/* --- evidence authority --------------------------------------- */}
            <Card>
              <CardHeader title="Evidence authority" description={gov.data.evidence_authority.source} />
              <CardBody className="space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[13px] text-[var(--text-secondary)]">Citable statuses:</span>
                  {gov.data.evidence_authority.citable_statuses.map((s) => (
                    <Badge key={s} tone="ok" size="xs">
                      {s}
                    </Badge>
                  ))}
                  <span className="ml-3 text-[13px] text-[var(--text-secondary)]">
                    Broadening ceiling per run:
                  </span>
                  <span className="tnum font-medium">
                    {gov.data.evidence_authority.broadening_ceiling_per_run}
                  </span>
                </div>
                <p className="text-[13px] leading-relaxed text-[var(--text-secondary)]">
                  {gov.data.evidence_authority.enforcement}
                </p>
                <p className="text-[13px] leading-relaxed text-[var(--text-secondary)]">
                  {gov.data.evidence_authority.cache_rule}
                </p>
              </CardBody>
            </Card>

            {/* --- authentication detail --------------------------------- */}
            <Card>
              <CardHeader title="Roles referenced by the domain" />
              <CardBody>
                <ul className="flex flex-wrap gap-2">
                  {gov.data.authentication.roles_referenced_by_the_domain.map((role) => (
                    <li
                      key={role}
                      className="rounded-[var(--radius-full)] border border-[var(--border-default)] px-2.5 py-1 text-[12px] text-[var(--text-secondary)]"
                    >
                      {role}
                    </li>
                  ))}
                </ul>
              </CardBody>
            </Card>
          </>
        )}
      </PageBody>
    </>
  );
}
