import React, { useState } from "react";
import { api } from "./api";
import {
  ActionNotice,
  Empty,
  Field,
  Heading,
  LoadState,
  Notice,
  useAction,
  useLoad,
} from "./components";
export function Students() {
  const state = useLoad(async () => ({
    batches: await api.all("/batches"),
    students: await api.all("/students"),
  }));
  const create = useAction(),
    upload = useAction(),
    mapping = useAction(),
    reset = useAction();
  const [result, setResult] = useState(null),
    [batch, setBatch] = useState(""),
    [selected, setSelected] = useState([]),
    [search, setSearch] = useState("");
  const data = state.data;
  return (
    <>
      <Heading
        eyebrow="COHORT MANAGEMENT"
        title="The right students. Together."
        description="Manage your roster and the batches that bring each exam to the right people."
      />
      <div className="two-columns">
        <section className="card padded">
          <h2>Create a batch</h2>
          <p className="muted">
            Create batches before importing your student roster.
          </p>
          <ActionNotice action={create} />
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = e.currentTarget,
                f = new FormData(form);
              create.run(async () => {
                await api.request("/batches", {
                  method: "POST",
                  body: { name: f.get("name"), year: Number(f.get("year")) },
                });
                form.reset();
                state.reload();
              }, "Batch created.");
            }}
          >
            <div className="form-grid">
              <Field
                label="Batch name"
                name="name"
                required
                maxLength={50}
                placeholder="e.g. CSE-A"
              />
              <Field
                label="Academic year"
                name="year"
                type="number"
                min={2000}
                max={2100}
                defaultValue={new Date().getFullYear()}
                required
              />
            </div>
            <button className="primary" disabled={create.busy}>
              {create.busy ? "Creating…" : "Create batch"}
            </button>
          </form>
        </section>
        <section className="card padded">
          <h2>Import students</h2>
          <p className="muted">
            CSV or Excel · Up to 1,000 rows · 2 MiB maximum
          </p>
          <p className="hint">
            Columns: <code>name,email,usn,batch</code>. Separate multiple batch
            names with <code>|</code>.
          </p>
          <ActionNotice action={upload} />
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const body = new FormData(e.currentTarget);
              setResult(null);
              upload.run(async () => {
                const r = await api.request("/students/bulk-import", {
                  method: "POST",
                  body,
                });
                setResult(r);
                state.reload();
              });
            }}
          >
            <Field
              label="Roster file"
              name="file"
              type="file"
              accept=".csv,.xlsx"
              required
            />
            <button className="primary" disabled={upload.busy}>
              {upload.busy ? "Importing…" : "Import roster"}
            </button>
          </form>
          {result && (
            <div className="import-result">
              <Notice>
                {result.created} student{result.created === 1 ? "" : "s"}{" "}
                imported. {result.errors.length} row
                {result.errors.length === 1 ? "" : "s"} rejected.
              </Notice>
              {!!result.errors.length && (
                <ul aria-label="Import row errors">
                  {result.errors.map((x) => (
                    <li key={x.row}>
                      <strong>Row {x.row}:</strong> {x.reason}
                    </li>
                  ))}
                </ul>
              )}
              <p className="hint">
                Imported students need a password-reset email before their first
                sign-in.
              </p>
            </div>
          )}
        </section>
      </div>
      <LoadState state={state}>
        {data && (
          <>
            <section className="card padded">
              <div className="section-title">
                <h2>
                  Batches <span className="count">{data.batches.length}</span>
                </h2>
              </div>
              {!data.batches.length ? (
                <Empty>No batches yet. Create one above.</Empty>
              ) : (
                <div className="batch-grid">
                  {data.batches.map((b) => (
                    <button
                      className={
                        batch === b.id ? "batch-card selected" : "batch-card"
                      }
                      key={b.id}
                      onClick={() => {
                        setBatch(b.id);
                        setSelected([]);
                        mapping.clear();
                      }}
                    >
                      <span>{b.name}</span>
                      <strong>
                        {b.student_count} <small>students</small>
                      </strong>
                      <small>Academic year {b.year}</small>
                    </button>
                  ))}
                </div>
              )}
              {batch && (
                <div className="membership">
                  <h3>
                    Add students to{" "}
                    {data.batches.find((b) => b.id === batch)?.name}
                  </h3>
                  <p className="hint">
                    Students can belong to several batches. Existing memberships
                    are preserved.
                  </p>
                  <ActionNotice action={mapping} />
                  <div className="checkbox-list">
                    {data.students.map((s) => (
                      <label key={s.id}>
                        <input
                          type="checkbox"
                          disabled={s.batch_ids.includes(batch)}
                          checked={
                            s.batch_ids.includes(batch) ||
                            selected.includes(s.id)
                          }
                          onChange={(e) =>
                            setSelected((ids) =>
                              e.target.checked
                                ? [...ids, s.id]
                                : ids.filter((id) => id !== s.id),
                            )
                          }
                        />
                        <span>
                          {s.name}{" "}
                          <small>
                            {s.usn}{" "}
                            {s.batch_ids.includes(batch)
                              ? "· Already a member"
                              : ""}
                          </small>
                        </span>
                      </label>
                    ))}
                  </div>
                  <button
                    className="primary"
                    disabled={mapping.busy || !selected.length}
                    onClick={() =>
                      mapping.run(async () => {
                        await api.request(`/batches/${batch}/students`, {
                          method: "POST",
                          body: { student_ids: selected },
                        });
                        setSelected([]);
                        state.reload();
                      }, "Memberships saved.")
                    }
                  >
                    Add selected students ({selected.length})
                  </button>
                </div>
              )}
            </section>
            <section className="card">
              <div className="section-title padded">
                <h2>
                  Student roster{" "}
                  <span className="count">{data.students.length}</span>
                </h2>
                <Field
                  label="Search students"
                  placeholder="Name, email or USN"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <div className="padded notice-area">
                <ActionNotice action={reset} />
              </div>
              {!data.students.filter((s) =>
                `${s.name} ${s.email} ${s.usn}`
                  .toLowerCase()
                  .includes(search.toLowerCase()),
              ).length ? (
                <Empty>No students found.</Empty>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Student</th>
                        <th>USN</th>
                        <th>Batches</th>
                        <th>Account</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.students
                        .filter((s) =>
                          `${s.name} ${s.email} ${s.usn}`
                            .toLowerCase()
                            .includes(search.toLowerCase()),
                        )
                        .map((s) => (
                          <tr key={s.id}>
                            <td>
                              <strong>{s.name}</strong>
                              <small>{s.email}</small>
                            </td>
                            <td>{s.usn || "—"}</td>
                            <td>
                              {s.batch_ids
                                .map(
                                  (id) =>
                                    data.batches.find((b) => b.id === id)?.name,
                                )
                                .filter(Boolean)
                                .join(", ") || "No batch"}
                            </td>
                            <td>
                              <span className="badge">
                                {s.must_reset_password
                                  ? "Reset required"
                                  : "Ready"}
                              </span>
                            </td>
                            <td>
                              <button
                                className="quiet"
                                disabled={reset.busy}
                                onClick={() => {
                                  if (
                                    window.confirm(
                                      `Send a password-reset email to ${s.email}? This signs the student out of all sessions.`,
                                    )
                                  )
                                    reset.run(async () => {
                                      await api.request(
                                        `/auth/students/${s.id}/reset-password`,
                                        { method: "POST", body: {} },
                                      );
                                      state.reload();
                                    }, "Password-reset email sent. The link is valid for one hour.");
                                }}
                              >
                                Send reset email
                              </button>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </LoadState>
    </>
  );
}
