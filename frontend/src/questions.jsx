import React, { useState } from "react";
import { api } from "./api";
import {
  ActionNotice,
  Empty,
  Field,
  Heading,
  LoadState,
  useAction,
  useLoad,
} from "./components";
const blank = () => ({
  text: "",
  subject: "",
  topic: "",
  difficulty: "EASY",
  default_marks: "2.00",
  negative_marks: "0.00",
  options: [
    { text: "", is_correct: true },
    { text: "", is_correct: false },
  ],
});
export function QuestionEditor({ question, onSaved, onCancel }) {
  const [form, setForm] = useState(() =>
    question ? structuredClone(question) : blank(),
  );
  const action = useAction();
  const change = (name, value) => setForm((f) => ({ ...f, [name]: value }));
  const option = (i, name, value) =>
    setForm((f) => ({
      ...f,
      options: f.options.map((o, j) => (j === i ? { ...o, [name]: value } : o)),
    }));
  return (
    <section className="card editor">
      <div className="section-title">
        <h2>{question ? "Edit question" : "New question"}</h2>
        <button className="quiet" onClick={onCancel}>
          Cancel
        </button>
      </div>
      <ActionNotice action={action} />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          action.run(async () => {
            if (form.options.filter((o) => o.is_correct).length !== 1)
              throw new Error("Choose exactly one correct answer.");
            if (
              new Set(form.options.map((o) => o.text.trim().toLowerCase()))
                .size !== form.options.length
            )
              throw new Error("Each option must have distinct text.");
            await api.request(
              question ? `/questions/${question.id}` : "/questions",
              { method: question ? "PUT" : "POST", body: form },
            );
            onSaved();
          });
        }}
      >
        <Field label="Question text">
          <textarea
            required
            maxLength={10000}
            value={form.text}
            onChange={(e) => change("text", e.target.value)}
            rows={3}
          />
        </Field>
        <div className="form-grid">
          <Field
            label="Subject"
            required
            maxLength={50}
            value={form.subject}
            onChange={(e) => change("subject", e.target.value)}
          />
          <Field
            label="Topic"
            required
            maxLength={50}
            value={form.topic}
            onChange={(e) => change("topic", e.target.value)}
          />
          <Field label="Difficulty">
            <select
              value={form.difficulty}
              onChange={(e) => change("difficulty", e.target.value)}
            >
              {["EASY", "MEDIUM", "HARD"].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </Field>
          <Field
            label="Marks"
            type="number"
            min="0.01"
            max="999.99"
            step="0.01"
            required
            value={form.default_marks}
            onChange={(e) => change("default_marks", e.target.value)}
          />
          <Field
            label="Penalty for wrong answer"
            type="number"
            min="0"
            max="999.99"
            step="0.01"
            required
            value={form.negative_marks}
            onChange={(e) => change("negative_marks", e.target.value)}
          />
        </div>
        <fieldset>
          <legend>
            Answer options{" "}
            <span className="muted">Choose one correct answer</span>
          </legend>
          {form.options.map((o, i) => (
            <div className="option-row" key={i}>
              <input
                type="radio"
                name="correct-option"
                aria-label={`Option ${i + 1} is correct`}
                checked={o.is_correct}
                onChange={() =>
                  change(
                    "options",
                    form.options.map((x, j) => ({ ...x, is_correct: j === i })),
                  )
                }
              />
              <Field
                label={`Option ${i + 1}`}
                required
                maxLength={2000}
                value={o.text}
                onChange={(e) => option(i, "text", e.target.value)}
              />
              <button
                type="button"
                className="quiet danger"
                disabled={form.options.length <= 2}
                aria-label={`Remove option ${i + 1}`}
                onClick={() =>
                  change(
                    "options",
                    form.options.filter((_, j) => j !== i),
                  )
                }
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            className="secondary"
            disabled={form.options.length >= 6}
            onClick={() =>
              change("options", [
                ...form.options,
                { text: "", is_correct: false },
              ])
            }
          >
            + Add option
          </button>
        </fieldset>
        <div className="form-actions">
          <span className="hint">
            Questions used in an exam cannot be edited.
          </span>
          <button className="primary" disabled={action.busy}>
            {action.busy ? "Saving…" : "Save question"}
          </button>
        </div>
      </form>
    </section>
  );
}
export function Questions() {
  const [filters, setFilters] = useState({}),
    [page, setPage] = useState(1),
    [editor, setEditor] = useState(null),
    [notice, setNotice] = useState("");
  const query = new URLSearchParams({ ...filters, page }).toString();
  const state = useLoad(() => api.request("/questions?" + query), [query]);
  const action = useAction();
  return (
    <>
      <Heading
        eyebrow="QUESTION LIBRARY"
        title="A stronger question bank."
        description="Create, organise and reuse questions across your assessments."
      >
        <button
          className="primary"
          onClick={() => {
            setNotice("");
            setEditor({});
          }}
        >
          + New question
        </button>
      </Heading>
      {notice && (
        <p className="notice success" role="status">
          {notice}
        </p>
      )}
      <ActionNotice action={action} />
      {editor && (
        <QuestionEditor
          key={editor.id || "new"}
          question={editor.id ? editor : null}
          onCancel={() => setEditor(null)}
          onSaved={() => {
            setEditor(null);
            setNotice("Question saved.");
            state.reload();
          }}
        />
      )}
      <section className="card">
        <form
          className="filter-bar"
          onSubmit={(e) => {
            e.preventDefault();
            const data = new FormData(e.currentTarget);
            setFilters(
              Object.fromEntries([...data.entries()].filter(([, v]) => v)),
            );
            setPage(1);
          }}
        >
          <Field
            label="Filter by subject"
            name="subject"
            placeholder="All subjects"
          />
          <Field
            label="Filter by topic"
            name="topic"
            placeholder="All topics"
          />
          <Field label="Filter by difficulty">
            <select name="difficulty">
              <option value="">All levels</option>
              {["EASY", "MEDIUM", "HARD"].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </Field>
          <button className="secondary">Apply filters</button>
          <button
            type="reset"
            className="quiet"
            onClick={() => {
              setFilters({});
              setPage(1);
            }}
          >
            Clear
          </button>
        </form>
        <LoadState state={state}>
          {state.data && (
            <>
              <div className="section-title padded">
                <h2>
                  Questions <span className="count">{state.data.count}</span>
                </h2>
                <span className="muted">Page {page}</span>
              </div>
              {!state.data.results.length ? (
                <Empty>No questions match these filters.</Empty>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Question</th>
                        <th>Subject / topic</th>
                        <th>Difficulty</th>
                        <th>Marks</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {state.data.results.map((q) => (
                        <tr key={q.id}>
                          <td className="question-cell">{q.text}</td>
                          <td>
                            {q.subject}
                            <small>{q.topic}</small>
                          </td>
                          <td>
                            <span
                              className={`badge ${q.difficulty.toLowerCase()}`}
                            >
                              {q.difficulty}
                            </span>
                          </td>
                          <td>
                            {q.default_marks}
                            <small>−{q.negative_marks} penalty</small>
                          </td>
                          <td>
                            <div className="row-actions">
                              <button
                                className="quiet"
                                onClick={() => setEditor(q)}
                              >
                                Edit
                              </button>
                              <button
                                className="quiet danger"
                                disabled={action.busy}
                                onClick={() => {
                                  if (
                                    window.confirm(
                                      "Delete this unused question? This cannot be undone.",
                                    )
                                  )
                                    action.run(async () => {
                                      await api.request(`/questions/${q.id}`, {
                                        method: "DELETE",
                                      });
                                      if (
                                        state.data.results.length === 1 &&
                                        page > 1
                                      )
                                        setPage(page - 1);
                                      else state.reload();
                                    }, "Question deleted.");
                                }}
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="pagination">
                <button
                  className="secondary"
                  disabled={!state.data.previous}
                  onClick={() => setPage((p) => p - 1)}
                >
                  ← Previous
                </button>
                <button
                  className="secondary"
                  disabled={!state.data.next}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next →
                </button>
              </div>
            </>
          )}
        </LoadState>
      </section>
    </>
  );
}
