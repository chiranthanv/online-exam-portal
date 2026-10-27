import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import { ActionNotice, Field, Notice, useAction } from "./components";
import { Questions } from "./questions";
import { Students } from "./students";
import { Exams, AvailableExams } from "./exams";
import "./style.css";

function SignIn({ onLogin, initialError }) {
  const action = useAction();
  return (
    <main className="auth-shell">
      <section className="auth-story">
        <a className="brand" href="/">
          e<span>Exam Portal</span>
        </a>
        <p className="eyebrow light">A little preparation. A better exam.</p>
        <h1>
          Your exams,
          <br />
          thoughtfully organised.
        </h1>
        <p>
          One workspace for your question bank, student cohorts and upcoming
          assessments.
        </p>
        <div className="story-foot">
          TEAM 15 <span>Online Exam Portal</span>
        </div>
      </section>
      <section className="auth-form">
        <div className="auth-inner">
          <span className="pill">Welcome back</span>
          <h2>Sign in to your workspace</h2>
          <p className="muted">
            Use the email registered with your institution.
          </p>
          {initialError && <Notice error>{initialError}</Notice>}
          <ActionNotice action={action} />
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = new FormData(e.currentTarget);
              action.run(async () =>
                onLogin(
                  await api.login(form.get("email"), form.get("password")),
                ),
              );
            }}
          >
            <Field
              label="Email address"
              name="email"
              type="email"
              autoComplete="username"
              required
            />
            <Field
              label="Password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              maxLength={256}
            />
            <button className="primary wide" disabled={action.busy}>
              {action.busy ? "Signing in…" : "Sign in →"}
            </button>
          </form>
          <p className="hint">
            Need a password reset? Contact your faculty administrator for a
            secure email link.
          </p>
        </div>
      </section>
    </main>
  );
}
function ResetPassword() {
  const [token] = useState(
    () => new URLSearchParams(location.search).get("token") || "",
  );
  const [done, setDone] = useState(false);
  const action = useAction();
  useEffect(() => {
    history.replaceState(null, "", "/reset-password");
  }, []);
  return (
    <main className="reset-shell">
      <section className="card reset-card">
        <a href="/" className="brand dark">
          e<span>Exam Portal</span>
        </a>
        <h1>Set your password</h1>
        {done ? (
          <>
            <Notice>Password updated. You can now sign in.</Notice>
            <a className="primary button-link" href="/">
              Back to sign in
            </a>
          </>
        ) : !token ? (
          <Notice error>
            This link is missing its reset token. Open the original email link,
            or ask your administrator for a new one.
          </Notice>
        ) : (
          <>
            <p className="muted">
              Use at least 10 characters. This email link expires after one hour
              and works once.
            </p>
            <ActionNotice action={action} />
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const f = new FormData(e.currentTarget);
                action.run(async () => {
                  if (f.get("password") !== f.get("confirm"))
                    throw new Error("Passwords do not match.");
                  await api.reset(token, f.get("password"));
                  setDone(true);
                });
              }}
            >
              <Field
                label="New password"
                name="password"
                type="password"
                minLength={10}
                maxLength={256}
                autoComplete="new-password"
                required
              />
              <Field
                label="Confirm password"
                name="confirm"
                type="password"
                minLength={10}
                maxLength={256}
                autoComplete="new-password"
                required
              />
              <button className="primary" disabled={action.busy}>
                {action.busy ? "Saving…" : "Set password"}
              </button>
            </form>
          </>
        )}
      </section>
    </main>
  );
}
function Workspace({ user, onLogout }) {
  const [page, setPage] = useState(
    user.role === "ADMIN" ? "exams" : "available",
  );
  const action = useAction();
  const admin = user.role === "ADMIN";
  const links = admin
    ? [
        ["exams", "Exams", "01"],
        ["questions", "Question bank", "02"],
        ["students", "Students & batches", "03"],
      ]
    : [["available", "Available exams", "01"]];
  return (
    <div className="workspace">
      <a className="skip-link" href="#content">
        Skip to main content
      </a>
      <aside className="sidebar">
        <a className="brand" href="/">
          e<span>Exam Portal</span>
        </a>
        <p className="nav-label">
          {admin ? "FACULTY WORKSPACE" : "STUDENT WORKSPACE"}
        </p>
        <nav aria-label="Main navigation">
          {links.map(([id, label, num]) => (
            <button
              key={id}
              className={page === id ? "nav-item active" : "nav-item"}
              aria-current={page === id ? "page" : undefined}
              onClick={() => setPage(id)}
            >
              <span>{num}</span>
              {label}
              <b>↗</b>
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <span className="status-dot" /> Ready for preparation
          <p>Keep your cohorts, questions and schedules in one place.</p>
        </div>
        <div className="profile">
          <div className="avatar">{user.name.slice(0, 1) || "U"}</div>
          <div>
            <strong>{user.name || user.email}</strong>
            <small>{admin ? "Faculty administrator" : "Student"}</small>
          </div>
        </div>
        <button
          className="logout"
          disabled={action.busy}
          onClick={() =>
            action.run(async () => {
              await api.logout();
              onLogout();
            })
          }
        >
          Sign out
        </button>
      </aside>
      <div className="main-shell">
        <div className="topbar">
          <span>
            Workspace <span className="slash">/</span>{" "}
            {links.find((x) => x[0] === page)?.[1]}
          </span>
          <span className="top-tag">
            {admin ? "Faculty access" : "Student access"}
          </span>
        </div>
        <main id="content" tabIndex={-1}>
          <ActionNotice action={action} />
          {page === "questions" && admin ? (
            <Questions />
          ) : page === "students" && admin ? (
            <Students />
          ) : page === "exams" && admin ? (
            <Exams />
          ) : (
            <AvailableExams />
          )}
        </main>
        <footer>
          Online Exam Portal <span>Team 15 · Built for focused assessment</span>
        </footer>
      </div>
    </div>
  );
}
function App() {
  const [user, setUser] = useState(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState("");
  const reset = location.pathname === "/reset-password";
  useEffect(() => {
    const unsubscribe = api.onExpired(() => {
      setUser(null);
      setError("Your session ended. Please sign in again.");
    });
    let active = true;
    if (!reset)
      api
        .restore()
        .then((u) => {
          if (active) setUser(u);
        })
        .catch((e) => {
          if (active) setError(e.message);
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    return () => {
      active = false;
      unsubscribe();
    };
  }, []);
  if (reset) return <ResetPassword />;
  if (loading)
    return (
      <div className="boot" role="status">
        Opening your workspace…
      </div>
    );
  return user ? (
    <Workspace
      key={user.id}
      user={user}
      onLogout={() => {
        setUser(null);
        setError("");
      }}
    />
  ) : (
    <SignIn
      initialError={error}
      onLogin={(u) => {
        setError("");
        setUser(u);
      }}
    />
  );
}
createRoot(document.getElementById("root")).render(<App />);
