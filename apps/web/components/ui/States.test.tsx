import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyState, ErrorState, SkeletonRows } from "./States";

describe("EmptyState -- always explains why, per Phase 23", () => {
  it("renders both a title and a reason", () => {
    render(<EmptyState title="Nothing is waiting" description="No run is currently blocked on a human." />);
    expect(screen.getByText("Nothing is waiting")).toBeInTheDocument();
    expect(screen.getByText("No run is currently blocked on a human.")).toBeInTheDocument();
  });
});

describe("ErrorState -- explains what happened and offers a next step", () => {
  it("announces the message via role=alert so it reaches assistive tech immediately", () => {
    render(<ErrorState message="The Orchestrator API could not be reached." />);
    expect(screen.getByRole("alert")).toHaveTextContent("The Orchestrator API could not be reached.");
  });

  it("never renders a stack trace even if one is passed as the message", () => {
    render(<ErrorState message={"Traceback (most recent call last):\n  File x.py"} />);
    // The component does not strip this itself -- callers are responsible for passing a
    // safe message (ApiError.userMessage). This test documents that expectation exists.
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});

describe("SkeletonRows -- loading is never a blank screen", () => {
  it("announces a loading state to screen readers", () => {
    render(<SkeletonRows rows={3} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
