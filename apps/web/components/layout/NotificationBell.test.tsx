import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { NotificationItem } from "@/lib/api";
import { NotificationBell } from "./NotificationBell";

/**
 * jsdom disables `localStorage` unless a real `url` is configured for the environment
 * (this project's vitest.config.mts does not set one), so the global is `undefined` here
 * -- the reason lib/auth/session.ts wraps every localStorage call in try/catch, and the
 * reason this bell does too. That defensive code makes the component silently "work"
 * (always reports everything as unread) without a real store behind it, which is enough
 * for most of the tests below but not for the one that specifically asserts persistence
 * survives a remount -- that one needs a real, if minimal, Storage implementation. Scoped
 * to this file rather than the shared vitest.setup.ts, since nothing else needs it.
 */
class MemoryStorage implements Storage {
  private store = new Map<string, string>();
  get length() {
    return this.store.size;
  }
  clear() {
    this.store.clear();
  }
  getItem(key: string) {
    return this.store.get(key) ?? null;
  }
  key(index: number) {
    return [...this.store.keys()][index] ?? null;
  }
  removeItem(key: string) {
    this.store.delete(key);
  }
  setItem(key: string, value: string) {
    this.store.set(key, value);
  }
}

vi.stubGlobal("localStorage", new MemoryStorage());

const getNotificationsMock = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, getNotifications: (...a: unknown[]) => getNotificationsMock(...a) };
});

function item(overrides: Partial<NotificationItem> = {}): NotificationItem {
  return {
    run_id: "R-web-1234",
    workflow: "batch_review",
    tier: "T2",
    severity: 3,
    evaluated_at: new Date().toISOString(),
    subject_id: "B-001",
    approver_roles: ["EU Qualified Person"],
    ...overrides,
  };
}

beforeEach(() => {
  getNotificationsMock.mockReset();
  getNotificationsMock.mockResolvedValue([]);
  localStorage.clear();
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("NotificationBell", () => {
  it("shows no unread badge when there is nothing to report", async () => {
    render(<NotificationBell />);
    await waitFor(() => expect(getNotificationsMock).toHaveBeenCalled());

    expect(screen.getByRole("button", { name: /^notifications$/i })).toBeInTheDocument();
  });

  it("shows an unread count badge for new escalations", async () => {
    getNotificationsMock.mockResolvedValue([item(), item({ run_id: "R-web-5678", tier: "T3", severity: 4 })]);
    render(<NotificationBell />);

    expect(await screen.findByRole("button", { name: /notifications, 2 unread/i })).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("opens a list of recent escalations and links each to its run", async () => {
    const user = userEvent.setup();
    getNotificationsMock.mockResolvedValue([item()]);
    render(<NotificationBell />);
    await screen.findByRole("button", { name: /1 unread/i });

    await user.click(screen.getByRole("button", { name: /notifications/i }));

    expect(screen.getByRole("menu", { name: /escalation notifications/i })).toBeInTheDocument();
    const link = screen.getByRole("link", { name: /gxp batch review.*B-001/i });
    expect(link).toHaveAttribute("href", "/decisions/R-web-1234");
  });

  it("labels severity 4 as Expired and severity 3 as Escalation due", async () => {
    getNotificationsMock.mockResolvedValue([
      item({ run_id: "R-t2", tier: "T2", severity: 3 }),
      item({ run_id: "R-t3", tier: "T3", severity: 4 }),
    ]);
    const user = userEvent.setup();
    render(<NotificationBell />);
    await screen.findByRole("button", { name: /2 unread/i });
    await user.click(screen.getByRole("button", { name: /notifications/i }));

    expect(screen.getByText("Escalation due")).toBeInTheDocument();
    expect(screen.getByText("Expired")).toBeInTheDocument();
  });

  it("says plainly when a run's subject id is no longer known", async () => {
    getNotificationsMock.mockResolvedValue([item({ subject_id: null, approver_roles: null })]);
    const user = userEvent.setup();
    render(<NotificationBell />);
    await screen.findByRole("button", { name: /1 unread/i });
    await user.click(screen.getByRole("button", { name: /notifications/i }));

    // Falls back to the run id when the subject id is unknown, and says the approver
    // isn't on file rather than showing nothing.
    expect(screen.getByText("R-web-1234")).toBeInTheDocument();
    expect(screen.getByText(/approver not on file/i)).toBeInTheDocument();
  });

  it("says plainly when nothing has escalated", async () => {
    const user = userEvent.setup();
    render(<NotificationBell />);
    await waitFor(() => expect(getNotificationsMock).toHaveBeenCalled());
    await user.click(screen.getByRole("button", { name: /notifications/i }));

    expect(screen.getByText(/nothing has escalated recently/i)).toBeInTheDocument();
  });

  it("clears the unread badge on open, and remembers across a remount", async () => {
    /**
     * "Unread" is deliberately a browser-local concept (localStorage, no server-side
     * per-user read state) -- this asserts that persistence actually works, not just that
     * the badge clears in the moment.
     */
    const user = userEvent.setup();
    getNotificationsMock.mockResolvedValue([item()]);
    const { unmount } = render(<NotificationBell />);
    await screen.findByRole("button", { name: /1 unread/i });

    await user.click(screen.getByRole("button", { name: /notifications/i }));
    await waitFor(() => expect(screen.getByRole("button", { name: /^notifications$/i })).toBeInTheDocument());
    unmount();

    render(<NotificationBell />);
    await waitFor(() => expect(getNotificationsMock).toHaveBeenCalled());
    expect(screen.getByRole("button", { name: /^notifications$/i })).toBeInTheDocument();
    expect(screen.queryByText("1")).not.toBeInTheDocument();
  });

  it("closes when Escape is pressed", async () => {
    const user = userEvent.setup();
    getNotificationsMock.mockResolvedValue([item()]);
    render(<NotificationBell />);
    await screen.findByRole("button", { name: /1 unread/i });

    await user.click(screen.getByRole("button", { name: /notifications/i }));
    expect(screen.getByRole("menu")).toBeInTheDocument();

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it("never claims to decide anything -- states it is visibility only", async () => {
    const user = userEvent.setup();
    getNotificationsMock.mockResolvedValue([item()]);
    render(<NotificationBell />);
    await screen.findByRole("button", { name: /1 unread/i });
    await user.click(screen.getByRole("button", { name: /notifications/i }));

    expect(screen.getByText(/nothing here decides anything/i)).toBeInTheDocument();
  });
});
