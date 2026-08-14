import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { EvidenceCatalogItem } from "@/lib/api";
import { EvidenceCard } from "./EvidenceCard";

function item(overrides: Partial<EvidenceCatalogItem>): EvidenceCatalogItem {
  return {
    evidence_id: "K-001",
    source: "SOME_POLICY.md",
    status: "approved",
    citable: true,
    authority: "NovaCura Global Policy",
    jurisdiction: "Global",
    effective_date: "2026-01-01",
    supersedes: null,
    superseded_by: null,
    content_excerpt: "",
    ...overrides,
  };
}

describe("EvidenceCard -- authority states are never visually equivalent (Phase 9)", () => {
  it("labels an approved, citable item AUTHORITATIVE", () => {
    render(<EvidenceCard item={item({ status: "approved", citable: true })} />);
    expect(screen.getByText("AUTHORITATIVE")).toBeInTheDocument();
  });

  it("labels an untrusted item UNTRUSTED and states it cannot be relied upon", () => {
    render(<EvidenceCard item={item({ status: "untrusted", citable: false })} />);
    expect(screen.getByText("UNTRUSTED")).toBeInTheDocument();
    expect(screen.getByText(/no run can cite this, and neither should you/i)).toBeInTheDocument();
  });

  it("labels a superseded item SUPERSEDED and names its replacement when known", () => {
    render(
      <EvidenceCard
        item={item({ status: "superseded", citable: false, superseded_by: "K-006" })}
      />,
    );
    expect(screen.getByText("SUPERSEDED")).toBeInTheDocument();
    expect(screen.getByText("K-006")).toBeInTheDocument();
  });

  it("labels local_approved as NOT CITABLE, not AUTHORITATIVE, even though it reads as approved", () => {
    render(<EvidenceCard item={item({ status: "local_approved", citable: false })} />);
    expect(screen.getByText("NOT CITABLE")).toBeInTheDocument();
    expect(screen.queryByText("AUTHORITATIVE")).not.toBeInTheDocument();
  });

  it("shows the unmissable warning line for every non-citable state, and for no citable state", () => {
    const { rerender } = render(<EvidenceCard item={item({ status: "untrusted", citable: false })} />);
    expect(screen.getByText(/cannot be relied upon|no run can cite/i)).toBeInTheDocument();

    rerender(<EvidenceCard item={item({ status: "approved", citable: true })} />);
    expect(screen.queryByText(/no run can cite/i)).not.toBeInTheDocument();
  });
});
