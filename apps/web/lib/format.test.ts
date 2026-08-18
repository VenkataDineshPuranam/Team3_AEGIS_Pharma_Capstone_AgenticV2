import { describe, expect, it } from "vitest";
import { evidenceAuthority, evidenceTone, formatAge, isHumanPrecedent, terminalStateTone } from "./format";

describe("evidenceAuthority", () => {
  it("labels untrusted items UNTRUSTED regardless of the citable flag", () => {
    expect(evidenceAuthority("untrusted", false)).toBe("UNTRUSTED");
  });

  it("labels superseded items SUPERSEDED even if citable were somehow true", () => {
    expect(evidenceAuthority("superseded", true)).toBe("SUPERSEDED");
  });

  it("labels a non-citable status outside the known set NOT CITABLE", () => {
    // The exact case that would expose a hand-restated rule: local_approved reads as
    // approved to a human but is not in evidence_retrieve's citable set.
    expect(evidenceAuthority("local_approved", false)).toBe("NOT CITABLE");
  });

  it("labels an approved, citable item AUTHORITATIVE", () => {
    expect(evidenceAuthority("approved", true)).toBe("AUTHORITATIVE");
  });

  it("labels a draft, citable item DRAFT, not AUTHORITATIVE", () => {
    expect(evidenceAuthority("draft", true)).toBe("DRAFT");
  });

  it("keeps human precedent as DRAFT rather than a new authority state", () => {
    expect(evidenceAuthority("draft", true)).toBe("DRAFT");
    expect(isHumanPrecedent("human_precedent/R-prior.md")).toBe(true);
    expect(isHumanPrecedent("SOP.md", "human_precedent")).toBe(true);
    expect(isHumanPrecedent("SOP.md", "NovaCura Global Policy")).toBe(false);
  });

  it("never returns AUTHORITATIVE for a non-citable item", () => {
    for (const status of ["untrusted", "superseded", "local_approved", "draft", "approved"]) {
      const authority = evidenceAuthority(status, false);
      if (status !== "untrusted" && status !== "superseded") {
        expect(authority).toBe("NOT CITABLE");
      }
      expect(authority).not.toBe("AUTHORITATIVE");
    }
  });
});

describe("evidenceTone", () => {
  it("gives every authority state a distinct tone", () => {
    const tones = (
      ["AUTHORITATIVE", "DRAFT", "UNTRUSTED", "SUPERSEDED", "NOT CITABLE"] as const
    ).map(evidenceTone);
    expect(new Set(tones).size).toBe(tones.length);
  });
});

describe("terminalStateTone", () => {
  it("maps blocked to the blocked tone, never to ok", () => {
    expect(terminalStateTone("blocked")).toBe("blocked");
    expect(terminalStateTone("blocked")).not.toBe("ok");
  });

  it("maps an unrecognized state to neutral rather than throwing", () => {
    expect(terminalStateTone("some_future_state")).toBe("neutral");
  });
});

describe("formatAge", () => {
  it("returns an em-dash placeholder for a missing timestamp", () => {
    expect(formatAge(null)).toBe("—");
    expect(formatAge(undefined)).toBe("—");
  });

  it("formats a few seconds ago in seconds", () => {
    const now = new Date().toISOString();
    expect(formatAge(now)).toMatch(/^\d+s$/);
  });
});
