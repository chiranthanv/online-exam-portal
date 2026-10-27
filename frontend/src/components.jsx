import React, { useEffect, useState } from "react";
export function Notice({ error, children }) {
  return (
    <div
      className={error ? "notice error" : "notice success"}
      role={error ? "alert" : "status"}
    >
      {children}
    </div>
  );
}
export function Field({ label, children, ...props }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children || <input {...props} />}
    </label>
  );
}
export function useLoad(loader, deps = []) {
  const [state, set] = useState({ loading: true, data: null, error: "" });
  const [version, reload] = useState(0);
  useEffect(() => {
    let active = true;
    set({ loading: true, data: null, error: "" });
    loader()
      .then((data) => {
        if (active) set({ data, loading: false, error: "" });
      })
      .catch((e) => {
        if (active) set({ data: null, loading: false, error: e.message });
      });
    return () => {
      active = false;
    };
  }, [...deps, version]);
  return { ...state, reload: () => reload((v) => v + 1) };
}
export function LoadState({ state, children }) {
  if (state.loading)
    return (
      <p className="empty" role="status">
        Loading…
      </p>
    );
  if (state.error)
    return (
      <Notice error>
        {state.error}{" "}
        <button className="quiet" onClick={state.reload}>
          Try again
        </button>
      </Notice>
    );
  return children;
}
export function useAction() {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  async function run(action, success = "") {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await action();
      setMessage(success);
      return result;
    } catch (e) {
      setError(e.message);
      return undefined;
    } finally {
      setBusy(false);
    }
  }
  return {
    busy,
    error,
    message,
    run,
    clear: () => {
      setError("");
      setMessage("");
    },
  };
}
export function ActionNotice({ action }) {
  return (
    <>
      {action.error && <Notice error>{action.error}</Notice>}
      {action.message && <Notice>{action.message}</Notice>}
    </>
  );
}
export function Heading({ eyebrow, title, description, children }) {
  return (
    <header className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="muted">{description}</p>
      </div>
      {children}
    </header>
  );
}
export function Empty({ children }) {
  return <div className="empty">{children}</div>;
}
export const dateText = (value) =>
  new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
export function localInput(value) {
  const d = new Date(value);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}
