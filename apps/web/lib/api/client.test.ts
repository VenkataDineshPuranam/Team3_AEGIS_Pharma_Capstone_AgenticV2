import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, mutate, read } from "./client";

describe("client.mutate -- the no-retry-on-human-action guarantee", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("calls fetch exactly once, even when the request fails", async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError("network error"));
    vi.stubGlobal("fetch", fetchMock);

    await expect(mutate("/api/runs/R-1/decide", { action: "approved" })).rejects.toThrow(ApiError);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("calls fetch exactly once on a 500 response -- mutations are never retried", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "boom" }), { status: 500 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(mutate("/api/runs/R-1/decide", {})).rejects.toThrow();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("surfaces an ambiguous-outcome message when the network call itself fails", async () => {
    // ApprovalPanel reads this via `error.status === 0` and shows it as the dialog's
    // hint -- this is the message that tells a human their action's fate is unknown,
    // distinct from ApiError.userMessage's generic per-status summary.
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("network error")));
    try {
      await mutate("/api/runs/R-1/decide", {});
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).message).toMatch(/may or may not/i);
      expect((e as ApiError).status).toBe(0);
    }
  });

  it("propagates a 409 (already decided) without retrying", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ detail: "already decided" }), { status: 409 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(mutate("/api/runs/R-1/decide", {})).rejects.toMatchObject({ status: 409 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe("client.read -- retry is allowed only here, and only for 5xx/network", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("retries a 503 and succeeds once the dependency recovers", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("unavailable", { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const result = await read<{ ok: boolean }>("/api/queue");
    expect(result).toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("does not retry a 404 -- it is a definitive answer, not a transient failure", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ detail: "not found" }), { status: 404 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(read("/api/runs/R-x")).rejects.toMatchObject({ status: 404 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe("ApiError.userMessage -- never leaks backend internals", () => {
  it("drops a structured FastAPI validation body down to a generic sentence", () => {
    const err = new ApiError("HTTP 422", 422, undefined);
    expect(err.userMessage).not.toMatch(/loc|msg|type/);
  });

  it("never includes the word Traceback", () => {
    const err = new ApiError("HTTP 500", 500);
    expect(err.userMessage).not.toMatch(/Traceback/);
  });
});
