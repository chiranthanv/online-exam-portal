import { describe, expect, it, vi } from "vitest";
import { createApi } from "./api";
const reply = (data, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => data,
});
describe("browser authentication contract", () => {
  it("keeps JWT in memory, sends CSRF and includes cookies", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(reply({ csrf_token: "csrf" }))
      .mockResolvedValueOnce(reply({ access_token: "access" }))
      .mockResolvedValueOnce(reply({ id: "admin", role: "ADMIN" }));
    const api = createApi(fetcher);
    expect((await api.login("a@example.test", "password")).role).toBe("ADMIN");
    expect(fetcher.mock.calls[1][1]).toMatchObject({
      credentials: "include",
      headers: { "X-CSRFToken": "csrf" },
    });
    expect(fetcher.mock.calls[2][1].headers.Authorization).toBe(
      "Bearer access",
    );
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);
  });
  it("preserves session headers on protected attempt requests", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValue(reply({ attempt_id: "attempt-1" }));
    const api = createApi(fetcher);
    const headers = { "X-Exam-Session": "session-uuid" };
    await api.request("/attempts/attempt-1", { headers });
    expect(fetcher.mock.calls[0][1].headers["X-Exam-Session"]).toBe(
      "session-uuid",
    );
  });
  it("uses a single refresh request when concurrent protected calls expire", async () => {
    let refreshes = 0,
      release;
    const gate = new Promise((resolve) => {
      release = resolve;
    });
    const fetcher = vi.fn(async (path, options) => {
      if (path.endsWith("/csrf")) return reply({ csrf_token: "c" });
      if (path.endsWith("/login")) return reply({ access_token: "old" });
      if (path.endsWith("/me")) return reply({ id: "a" });
      if (path.endsWith("/refresh")) {
        refreshes++;
        await gate;
        return reply({ access_token: "new" });
      }
      return options.headers.Authorization === "Bearer new"
        ? reply({ ok: true })
        : reply({ detail: "Expired" }, 401);
    });
    const api = createApi(fetcher);
    await api.login("a@b.test", "password");
    const a = api.request("/questions"),
      b = api.request("/exams");
    await vi.waitFor(() => expect(refreshes).toBe(1));
    release();
    expect(await Promise.all([a, b])).toEqual([{ ok: true }, { ok: true }]);
    expect(refreshes).toBe(1);
  });
  it("clears authenticated state when refresh is rejected", async () => {
    const expired = vi.fn();
    const fetcher = vi.fn(async (path) =>
      path.endsWith("/csrf")
        ? reply({ csrf_token: "c" })
        : reply({ detail: "Expired" }, 401),
    );
    const api = createApi(fetcher);
    api.onExpired(expired);
    await expect(api.request("/questions")).rejects.toMatchObject({
      status: 401,
    });
    expect(expired).toHaveBeenCalledOnce();
  });
  it("treats absent refresh cookie as signed out", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(reply({ csrf_token: "c" }))
      .mockResolvedValueOnce(reply({}, 401));
    expect(await createApi(fetcher).restore()).toBe(null);
  });
  it("preserves partial-import errors on HTTP 207", async () => {
    const body = {
      created: 1,
      errors: [{ row: 3, reason: "Duplicate email." }],
    };
    const api = createApi(vi.fn().mockResolvedValue(reply(body, 207)));
    expect(
      await api.request("/students/bulk-import", {
        method: "POST",
        body: new FormData(),
      }),
    ).toEqual(body);
  });
  it("reports lockout with retry time", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(reply({ csrf_token: "c" }))
      .mockResolvedValueOnce(reply({ retry_after_seconds: 900 }, 423));
    await expect(createApi(fetcher).login("a@b.test", "bad")).rejects.toThrow(
      "15 minutes",
    );
  });
  it("handles HTML CSRF errors without a JSON crash", async () => {
    const api = createApi(
      vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => {
          throw new Error("HTML");
        },
      }),
    );
    await expect(api.request("/questions")).rejects.toThrow(
      "Request failed (403)",
    );
  });
  it("reports network failures without signing the user out", async () => {
    const expired = vi.fn(),
      api = createApi(vi.fn().mockRejectedValue(new Error("offline")));
    api.onExpired(expired);
    await expect(api.request("/questions")).rejects.toThrow("Cannot reach");
    expect(expired).not.toHaveBeenCalled();
  });
  it("follows every page for selectors", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(
        reply({
          results: [{ id: 1 }],
          next: "https://portal.example/api/v1/questions?page=2",
        }),
      )
      .mockResolvedValueOnce(reply({ results: [{ id: 2 }], next: null }));
    expect(await createApi(fetcher).all("/questions")).toEqual([
      { id: 1 },
      { id: 2 },
    ]);
    expect(fetcher.mock.calls[1][0]).toBe("/api/v1/questions?page=2");
  });
});
