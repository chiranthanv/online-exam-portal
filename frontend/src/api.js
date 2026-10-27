const ROOT = "/api/v1";
export class ApiError extends Error {
  constructor(status, data) {
    const describe = (value) =>
      Array.isArray(value)
        ? value.map(describe).join(" ")
        : value && typeof value === "object"
          ? Object.entries(value)
              .map(
                ([k, v]) =>
                  `${k === "detail" || k === "non_field_errors" ? "" : k + ": "}${describe(v)}`,
              )
              .join(" ")
          : String(value);
    super(
      status === 423
        ? `Account temporarily locked. Try again in ${Math.ceil((data.retry_after_seconds || 900) / 60)} minutes.`
        : describe(data),
    );
    this.status = status;
    this.data = data;
  }
}
export function createApi(fetcher = (...args) => fetch(...args)) {
  let access = null,
    csrf = null,
    refreshing = null,
    expired = () => {};
  async function raw(
    path,
    { method = "GET", body, auth = true, withCsrf = false } = {},
  ) {
    const headers = { Accept: "application/json" };
    if (access && auth) headers.Authorization = `Bearer ${access}`;
    if (withCsrf && csrf) headers["X-CSRFToken"] = csrf;
    if (body !== undefined && !(body instanceof FormData))
      headers["Content-Type"] = "application/json";
    let response;
    try {
      response = await fetcher(ROOT + path, {
        method,
        headers,
        credentials: "include",
        body:
          body === undefined
            ? undefined
            : body instanceof FormData
              ? body
              : JSON.stringify(body),
      });
    } catch {
      throw new ApiError(0, {
        detail: "Cannot reach the server. Check your connection and try again.",
      });
    }
    const data =
      response.status === 204
        ? null
        : responseType === "blob"
          ? await response.blob()
          : await response.json().catch(() => ({
              detail: `Request failed (${response.status}). Refresh the page and try again.`,
            }));
    if (!response.ok) {
      let errorData = data;
      if (responseType === "blob" && data instanceof Blob) {
        try {
          errorData = JSON.parse(await data.text());
        } catch {
          errorData = { detail: `Request failed (${response.status}).` };
        }
      }
      throw new ApiError(response.status, errorData);
    }
    return data;
  }
  async function getCsrf() {
    csrf = (await raw("/auth/csrf", { auth: false })).csrf_token;
  }
  async function refresh() {
    if (!refreshing)
      refreshing = (async () => {
        if (!csrf) await getCsrf();
        const result = await raw("/auth/refresh", {
          method: "POST",
          body: {},
          auth: false,
          withCsrf: true,
        });
        access = result.access_token;
      })().finally(() => {
        refreshing = null;
      });
    return refreshing;
  }
  async function request(path, options) {
    const tokenAtStart = access;
    try {
      return await raw(path, options);
    } catch (error) {
      if (error.status !== 401) throw error;
      try {
        // A concurrent request may already have rotated the access token.
        if (!access || access === tokenAtStart) await refresh();
        return await raw(path, options);
      } catch (failure) {
        if (failure.status === 401) {
          access = null;
          expired();
        }
        throw failure;
      }
    }
  }
  return {
    request,
    async download(path, filename) {
      const blob = await request(path, { responseType: "blob" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    },
    onExpired(handler) {
      expired = handler;
      return () => {
        expired = () => {};
      };
    },
    async restore() {
      try {
        await refresh();
        return await raw("/auth/me");
      } catch (error) {
        if (error.status === 401) {
          access = null;
          return null;
        }
        throw error;
      }
    },
    async login(email, password) {
      await getCsrf();
      const result = await raw("/auth/login", {
        method: "POST",
        body: { email, password },
        auth: false,
        withCsrf: true,
      });
      access = result.access_token;
      return await raw("/auth/me");
    },
    async logout() {
      await request("/auth/logout", {
        method: "POST",
        body: {},
        withCsrf: true,
      });
      access = null;
    },
    async reset(token, password) {
      await getCsrf();
      return raw("/auth/reset-password/confirm", {
        method: "POST",
        body: { token, password },
        auth: false,
        withCsrf: true,
      });
    },
    async all(path) {
      const items = [];
      for (let next = path; next; ) {
        const page = await request(next);
        items.push(...page.results);
        if (!page.next) break;
        const url = new URL(page.next, "http://pagination.local");
        if (!url.pathname.startsWith(ROOT + "/"))
          throw new Error("Unexpected pagination path.");
        next = url.pathname.slice(ROOT.length) + url.search;
      }
      return items;
    },
  };
}
export const api = createApi();
