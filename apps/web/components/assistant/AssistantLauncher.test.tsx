import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { setSession } from "@/lib/auth/session";
import { AssistantLauncher } from "./AssistantLauncher";

setSession({
  token: "test-token",
  user_id: "test_qp",
  display_name: "Test QP",
  role: "EU Qualified Person",
  expires_at: new Date(Date.now() + 3600_000).toISOString(),
});

let pathname = "/";
vi.mock("next/navigation", () => ({ usePathname: () => pathname }));

const askAboutRunMock = vi.fn();
const getQueueMock = vi.fn();
const getRunHistoryMock = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    askAboutRun: (...a: unknown[]) => askAboutRunMock(...a),
    getQueue: (...a: unknown[]) => getQueueMock(...a),
    getRunHistory: (...a: unknown[]) => getRunHistoryMock(...a),
  };
});

function queueEntry(runId: string, subjectId: string) {
  return {
    run_id: runId,
    workflow: "batch_review",
    subject_id: subjectId,
    requester_role: "EU Qualified Person",
    approver_roles: ["EU Qualified Person"],
    required_legs: [],
    approved_legs: [],
    draft_summary: null,
    draft_claims: [],
    created_at: new Date().toISOString(),
    evidence: [],
    domain_payload: null,
    evidence_accounting: null,
    hitl_timer: { tier: "T0", label: "On time", severity: 1, hours_elapsed: 0.1, hours_to_next_tier: 7.9 },
  };
}

beforeEach(() => {
  pathname = "/";
  askAboutRunMock.mockReset();
  getQueueMock.mockReset();
  getRunHistoryMock.mockReset();

  askAboutRunMock.mockResolvedValue({
    run_id: "R-1",
    record: { run_id: "R-1", subject_id: "B-001", workflow: "batch_review", status: "awaiting_human_decision" },
    next_steps: [{ step: "This run is paused awaiting a human decision.", owner: "EU QP", blocking: true }],
    summary: "A batch review run for B-001 is paused.",
    answer: "",
    next_steps_explanation: "",
    cites: [],
    llm_available: true,
    llm_unavailable_reason: null,
    guard: {
      prompt_guard_version: "1.0.0",
      input_verdict: "clear",
      output_verdict: "clear",
      input_hits: [],
      record_hits: [],
      output_hits: [],
      refused: false,
    },
  });
  getQueueMock.mockResolvedValue([queueEntry("R-1", "B-001"), queueEntry("R-2", "PV-2024-0881")]);
  getRunHistoryMock.mockResolvedValue({ items: [], total: 0, limit: 8, offset: 0 });
});

describe("AssistantLauncher", () => {
  it("offers the assistant from a page that is not a run detail page", async () => {
    /**
     * The regression this component exists for. The assistant was originally only a tab
     * on the run detail page, which made it unreachable from the overview, the queue, or
     * anywhere else an operator actually starts.
     */
    pathname = "/";
    render(<AssistantLauncher />);

    expect(screen.getByRole("button", { name: /ask about a record/i })).toBeInTheDocument();
  });

  it("prompts to search when the route does not identify a record, with nothing to click", async () => {
    const user = userEvent.setup();
    pathname = "/decisions";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));

    expect(await screen.findByText(/type an id above/i)).toBeInTheDocument();
    // No default browse list -- nothing is shown, and nothing has been asked, until the
    // operator actually types something.
    expect(screen.queryByText(/B-001/)).not.toBeInTheDocument();
    expect(askAboutRunMock).not.toHaveBeenCalled();
  });

  it("opens straight onto the run when the route already identifies one", async () => {
    /** Asking an operator to pick the record they are visibly looking at is friction. */
    const user = userEvent.setup();
    pathname = "/decisions/R-web-1234";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));

    await waitFor(() => expect(askAboutRunMock).toHaveBeenCalled());
    expect(askAboutRunMock.mock.calls[0][0]).toBe("R-web-1234");
    expect(screen.queryByText(/type an id above/i)).not.toBeInTheDocument();
  });

  it("treats /runs/<id> as a record too, but not the /runs list", async () => {
    const user = userEvent.setup();
    pathname = "/runs";
    const { unmount } = render(<AssistantLauncher />);
    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    expect(await screen.findByText(/type an id above/i)).toBeInTheDocument();
    unmount();

    pathname = "/runs/R-web-9999";
    render(<AssistantLauncher />);
    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    await waitFor(() => expect(askAboutRunMock).toHaveBeenCalled());
    expect(askAboutRunMock.mock.calls[0][0]).toBe("R-web-9999");
  });

  it("closes on Escape", async () => {
    const user = userEvent.setup();
    pathname = "/";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    expect(screen.getByRole("dialog", { name: /record assistant/i })).toBeInTheDocument();

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  // --- type-to-find, the only way to pick a record from a list page ----------

  it("shows nothing until the operator types, then finds a record by id", async () => {
    const user = userEvent.setup();
    pathname = "/";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    expect(screen.queryByText(/B-001/)).not.toBeInTheDocument();
    expect(screen.queryByText(/PV-2024-0881/)).not.toBeInTheDocument();

    await user.type(screen.getByLabelText(/search for a record/i), "PV-2024");

    expect(await screen.findByText(/PV-2024-0881/)).toBeInTheDocument();
    expect(screen.queryByText(/B-001/)).not.toBeInTheDocument();
  });

  it("matches by run id as well as subject id", async () => {
    const user = userEvent.setup();
    pathname = "/";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    await user.type(screen.getByLabelText(/search for a record/i), "R-2");

    expect(await screen.findByText(/PV-2024-0881/)).toBeInTheDocument();
    expect(screen.queryByText(/B-001/)).not.toBeInTheDocument();
  });

  it("does not query run history until there is something to search for", async () => {
    const user = userEvent.setup();
    pathname = "/";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    expect(getRunHistoryMock).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText(/search for a record/i), "B-EVIL");

    await waitFor(() =>
      expect(getRunHistoryMock).toHaveBeenCalledWith(
        expect.objectContaining({ search: "B-EVIL" }),
        expect.anything(),
      ),
    );
    // Debounced to one request, not one per keystroke.
    expect(getRunHistoryMock).toHaveBeenCalledTimes(1);
  });

  it("says plainly when a typed query matches nothing", async () => {
    const user = userEvent.setup();
    pathname = "/";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    await user.type(screen.getByLabelText(/search for a record/i), "no-such-record-xyz");

    expect(await screen.findByText(/no record matches that search/i)).toBeInTheDocument();
  });

  it("picking a search match asks about that record and opens the chat", async () => {
    const user = userEvent.setup();
    pathname = "/";
    render(<AssistantLauncher />);

    await user.click(screen.getByRole("button", { name: /ask about a record/i }));
    await user.type(screen.getByLabelText(/search for a record/i), "B-001");
    await user.click(await screen.findByText(/B-001/));

    await waitFor(() => expect(askAboutRunMock).toHaveBeenCalled());
    expect(askAboutRunMock.mock.calls[0][0]).toBe("R-1");
    expect(askAboutRunMock.mock.calls[0][1]).toBe("");
    expect(await screen.findByText(/A batch review run for B-001 is paused/)).toBeInTheDocument();
  });
});
