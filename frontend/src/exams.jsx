import React, { useEffect, useRef, useState } from "react";
import { api } from "./api";
import {
  ActionNotice,
  Empty,
  Field,
  Heading,
  LoadState,
  dateText,
  localInput,
  useAction,
  useLoad,
} from "./components";
export function ScheduleForm({ exam, onSaved, onCancel }) {
  const action = useAction();
  return (
    <section className="card padded">
      <div className="section-title">
        <h2>{exam ? "Edit schedule" : "Create an exam"}</h2>
        <button className="quiet" onClick={onCancel}>
          Cancel
        </button>
      </div>
      <ActionNotice action={action} />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          action.run(async () => {
            const body = {
              title: f.get("title"),
              duration_minutes: Number(f.get("duration")),
              ...Object.fromEntries(
                ["start_time", "end_time", "result_visible_from"].map((k) => [
                  k,
                  new Date(f.get(k)).toISOString(),
                ]),
              ),
            };
            if (new Date(body.end_time) <= new Date(body.start_time))
              throw new Error("End time must be after start time.");
            await api.request(exam ? `/exams/${exam.id}` : "/exams", {
              method: exam ? "PATCH" : "POST",
              body,
            });
            onSaved();
          });
        }}
      >
        <Field
          label="Exam title"
          name="title"
          defaultValue={exam?.title || ""}
          maxLength={150}
          required
        />
        <div className="form-grid">
          <Field
            label="Duration (minutes)"
            name="duration"
            type="number"
            min={1}
            max={1440}
            defaultValue={exam?.duration_minutes || 30}
            required
          />
          {[
            ["start_time", "Starts at"],
            ["end_time", "Ends at"],
            ["result_visible_from", "Results visible from"],
          ].map(([key, label]) => (
            <Field
              key={key}
              label={label}
              name={key}
              type="datetime-local"
              defaultValue={exam ? localInput(exam[key]) : ""}
              required
            />
          ))}
        </div>
        <p className="hint">
          Times use your device timezone (
          {Intl.DateTimeFormat().resolvedOptions().timeZone}). Schedule a future
          start to configure questions and batches.
        </p>
        <button className="primary" disabled={action.busy}>
          {action.busy ? "Saving…" : "Save schedule"}
        </button>
      </form>
    </section>
  );
}
function ExamConfiguration({ exam, onClose, onSaved }) {
  const state = useLoad(
    async () => ({
      questions: await api.all("/questions"),
      batches: await api.all("/batches"),
      selection: await api.request(`/exams/${exam.id}/questions`),
    }),
    [exam.id],
  );
  const [mode, setMode] = useState("manual"),
    [ids, setIds] = useState(null),
    [batches, setBatches] = useState(exam.batch_ids),
    [search, setSearch] = useState("");
  const action = useAction(),
    assign = useAction();
  const frozen = new Date(exam.start_time) <= new Date();
  const selected = ids || state.data?.selection.results.map((q) => q.id) || [];
  function move(id, delta) {
    const next = [...selected],
      i = next.indexOf(id),
      j = i + delta;
    if (j >= 0 && j < next.length) {
      [next[i], next[j]] = [next[j], next[i]];
      setIds(next);
    }
  }
  return (
    <section className="card padded configuration">
      <div className="section-title">
        <div>
          <p className="eyebrow">EXAM CONFIGURATION</p>
          <h2>{exam.title}</h2>
        </div>
        <button className="quiet" onClick={onClose}>
          Close
        </button>
      </div>
      {frozen && (
        <p className="notice">
          This exam has started. Its configuration is frozen.
        </p>
      )}
      <LoadState state={state}>
        {state.data && (
          <>
            <h3>1. Select questions</h3>
            <ActionNotice action={action} />
            <fieldset disabled={frozen || action.busy}>
              <div className="segmented">
                <label>
                  <input
                    type="radio"
                    name="selection-mode"
                    checked={mode === "manual"}
                    onChange={() => setMode("manual")}
                  />{" "}
                  Manual selection
                </label>
                <label>
                  <input
                    type="radio"
                    name="selection-mode"
                    checked={mode === "random"}
                    onChange={() => setMode("random")}
                  />{" "}
                  Random selection
                </label>
              </div>
              {mode === "manual" ? (
                <>
                  <Field
                    label="Find a question"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search question text, subject or topic"
                  />
                  <div className="checkbox-list questions-picker">
                    {state.data.questions
                      .filter((q) =>
                        `${q.text} ${q.subject} ${q.topic}`
                          .toLowerCase()
                          .includes(search.toLowerCase()),
                      )
                      .map((q) => (
                        <label key={q.id}>
                          <input
                            type="checkbox"
                            checked={selected.includes(q.id)}
                            onChange={(e) =>
                              setIds(
                                e.target.checked
                                  ? [...selected, q.id]
                                  : selected.filter((id) => id !== q.id),
                              )
                            }
                          />
                          <span>
                            {q.text}
                            <small>
                              {q.subject} · {q.difficulty} · {q.default_marks}{" "}
                              marks
                            </small>
                          </span>
                        </label>
                      ))}
                  </div>
                  <h4>Selected order ({selected.length})</h4>
                  <ol className="ordered-selection">
                    {selected.map((id, i) => (
                      <li key={id}>
                        <span>
                          {state.data.questions.find((q) => q.id === id)
                            ?.text || "Question"}
                        </span>
                        <button
                          type="button"
                          className="quiet"
                          disabled={!i}
                          aria-label={`Move question ${i + 1} up`}
                          onClick={() => move(id, -1)}
                        >
                          ↑
                        </button>
                        <button
                          type="button"
                          className="quiet"
                          disabled={i === selected.length - 1}
                          aria-label={`Move question ${i + 1} down`}
                          onClick={() => move(id, 1)}
                        >
                          ↓
                        </button>
                      </li>
                    ))}
                  </ol>
                  <button
                    className="primary"
                    disabled={!selected.length}
                    onClick={() =>
                      action.run(async () => {
                        const r = await api.request(
                          `/exams/${exam.id}/questions`,
                          {
                            method: "POST",
                            body: { mode: "manual", question_ids: selected },
                          },
                        );
                        onSaved();
                        return r;
                      }, "Question selection and total marks saved.")
                    }
                  >
                    Save question selection
                  </button>
                </>
              ) : (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const f = new FormData(e.currentTarget);
                    action.run(async () => {
                      const body = {
                        mode: "random",
                        random_count: Number(f.get("count")),
                      };
                      for (const k of ["subject", "topic"])
                        if (f.get(k)) body[k] = f.get(k);
                      if (f.get("mix") === "on") {
                        body.difficulty_mix = Object.fromEntries(
                          ["EASY", "MEDIUM", "HARD"].map((k) => [
                            k,
                            Number(f.get(k)),
                          ]),
                        );
                        if (
                          Object.values(body.difficulty_mix).reduce(
                            (a, b) => a + b,
                            0,
                          ) !== body.random_count
                        )
                          throw new Error(
                            "Difficulty counts must add up to the question count.",
                          );
                      }
                      await api.request(`/exams/${exam.id}/questions`, {
                        method: "POST",
                        body,
                      });
                      setIds(null);
                      state.reload();
                      onSaved();
                    }, "Random question selection and total marks saved.");
                  }}
                >
                  <div className="form-grid">
                    <Field
                      label="Number of questions"
                      name="count"
                      type="number"
                      min={1}
                      max={500}
                      defaultValue={5}
                      required
                    />
                    <Field
                      label="Subject filter"
                      name="subject"
                      maxLength={50}
                      placeholder="Any subject"
                    />
                    <Field
                      label="Topic filter"
                      name="topic"
                      maxLength={50}
                      placeholder="Any topic"
                    />
                  </div>
                  <label className="check-label">
                    <input name="mix" type="checkbox" /> Use an exact difficulty
                    mix
                  </label>
                  <div className="form-grid">
                    {["EASY", "MEDIUM", "HARD"].map((x) => (
                      <Field
                        key={x}
                        label={`${x} count`}
                        name={x}
                        type="number"
                        min={0}
                        max={500}
                        defaultValue={0}
                      />
                    ))}
                  </div>
                  <p className="hint">
                    This replaces the previous selection. Insufficient matching
                    questions leave it unchanged.
                  </p>
                  <button className="primary">Select random questions</button>
                </form>
              )}
            </fieldset>
            <hr />
            <h3>2. Assign batches</h3>
            <ActionNotice action={assign} />
            <fieldset disabled={frozen || assign.busy}>
              <div className="checkbox-list">
                {state.data.batches.map((b) => (
                  <label key={b.id}>
                    <input
                      type="checkbox"
                      checked={batches.includes(b.id)}
                      onChange={(e) =>
                        setBatches((ids) =>
                          e.target.checked
                            ? [...ids, b.id]
                            : ids.filter((id) => id !== b.id),
                        )
                      }
                    />
                    <span>
                      {b.name}
                      <small>
                        {b.student_count} students · {b.year}
                      </small>
                    </span>
                  </label>
                ))}
              </div>
              <button
                className="primary"
                disabled={!batches.length}
                onClick={() =>
                  assign.run(async () => {
                    await api.request(`/exams/${exam.id}/batches`, {
                      method: "POST",
                      body: { batch_ids: batches },
                    });
                    onSaved();
                  }, "Batch assignments saved.")
                }
              >
                Save batch assignments
              </button>
            </fieldset>
          </>
        )}
      </LoadState>
    </section>
  );
}
export function Exams() {
  const state = useLoad(() => api.all("/exams"));
  const [schedule, setSchedule] = useState(null),
    [configure, setConfigure] = useState(null);
  return (
    <>
      <Heading
        eyebrow="ASSESSMENT PLANNING"
        title="Make room for good exams."
        description="Prepare your schedule, choose questions and connect the right batches."
      >
        <button
          className="primary"
          onClick={() => {
            setSchedule({});
            setConfigure(null);
          }}
        >
          + Create exam
        </button>
      </Heading>
      {schedule && (
        <ScheduleForm
          key={schedule.id || "new"}
          exam={schedule.id ? schedule : null}
          onSaved={() => {
            setSchedule(null);
            state.reload();
          }}
          onCancel={() => setSchedule(null)}
        />
      )}
      <LoadState state={state}>
        {state.data && (
          <>
            <div className="stats">
              <div>
                <span>Total exams</span>
                <strong>{state.data.length.toString().padStart(2, "0")}</strong>
              </div>
              <div>
                <span>Upcoming</span>
                <strong>
                  {state.data
                    .filter((e) => new Date(e.start_time) > new Date())
                    .length.toString()
                    .padStart(2, "0")}
                </strong>
              </div>
              <div>
                <span>In the current window</span>
                <strong>
                  {state.data
                    .filter(
                      (e) =>
                        new Date(e.start_time) <= new Date() &&
                        new Date(e.end_time) > new Date(),
                    )
                    .length.toString()
                    .padStart(2, "0")}
                </strong>
              </div>
            </div>
            <section className="card">
              <div className="section-title padded">
                <h2>Your assessments</h2>
                <span className="muted">All schedules</span>
              </div>
              {!state.data.length ? (
                <Empty>No exams yet. Create your first assessment above.</Empty>
              ) : (
                <div className="exam-grid">
                  {state.data.map((e) => {
                    const started = new Date(e.start_time) <= new Date(),
                      ended = new Date(e.end_time) <= new Date();
                    return (
                      <article className="exam-card" key={e.id}>
                        <div className="section-title">
                          <span className="exam-icon">▤</span>
                          <span
                            className={`badge ${ended ? "" : started ? "easy" : "medium"}`}
                          >
                            {ended
                              ? "Window ended"
                              : started
                                ? "Available window"
                                : "Upcoming"}
                          </span>
                        </div>
                        <h3>{e.title}</h3>
                        <p className="muted">{dateText(e.start_time)}</p>
                        <div className="exam-metrics">
                          <span>
                            <strong>{e.duration_minutes}</strong> min
                          </span>
                          <span>
                            <strong>{e.question_count}</strong> questions
                          </span>
                          <span>
                            <strong>{e.total_marks}</strong> marks
                          </span>
                        </div>
                        <p className="hint">
                          {e.batch_ids.length} assigned batch
                          {e.batch_ids.length === 1 ? "" : "es"} · Ends{" "}
                          {dateText(e.end_time)}
                        </p>
                        <div className="row-actions">
                          <button
                            className="secondary"
                            onClick={() => {
                              setConfigure(e);
                              setSchedule(null);
                            }}
                          >
                            Configure exam
                          </button>
                          <button
                            className="quiet"
                            disabled={started}
                            onClick={() => {
                              setSchedule(e);
                              setConfigure(null);
                            }}
                          >
                            Edit schedule
                          </button>
                        </div>
                      </article>
                    );
                  })}
                </div>
              )}
            </section>
          </>
        )}
      </LoadState>
      {configure && (
        <ExamConfiguration
          key={configure.id}
          exam={configure}
          onClose={() => setConfigure(null)}
          onSaved={() => state.reload()}
        />
      )}
    </>
  );
}

function ExamAttemptRunner({ exam, onBack }) {
  const storageKey = `oep:attempt:${exam.exam_id}`;
  const [attempt, setAttempt] = useState(null);
  const [sessionId, setSessionId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [savingAnswers, setSavingAnswers] = useState({});
  const [submitPending, setSubmitPending] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [now, setNow] = useState(() => window.performance.now());
  const autoSubmitting = useRef(false);
  const deadlineMonotonicAt = useRef(null);

  useEffect(() => {
    let active = true;
    async function openOrResume() {
      setLoading(true);
      setError("");
      try {
        let saved = null;
        try {
          saved = JSON.parse(sessionStorage.getItem(storageKey) || "null");
        } catch {
          saved = null;
        }
        if (!saved?.session_id) {
          saved = { session_id: window.crypto.randomUUID() };
        }
        const headers = { "X-Exam-Session": saved.session_id };
        const data = saved.attempt_id
          ? await api.request(`/attempts/${saved.attempt_id}`, { headers })
          : await api.request(`/exams/${exam.exam_id}/attempt`, {
              method: "POST",
              body: { session_id: saved.session_id },
              headers,
            });
        saved.attempt_id = data.attempt_id;
        sessionStorage.setItem(storageKey, JSON.stringify(saved));
        if (active) {
          setSessionId(saved.session_id);
          deadlineMonotonicAt.current =
            window.performance.now() +
            Math.max(
              0,
              Date.parse(data.deadline_at) - Date.parse(data.server_now),
            );
          setAttempt(data);
        }
      } catch (e) {
        if (active) setError(e.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    openOrResume();
    return () => {
      active = false;
    };
  }, [storageKey, exam.exam_id]);

  useEffect(() => {
    const timer = window.setInterval(
      () => setNow(window.performance.now()),
      250,
    );
    return () => window.clearInterval(timer);
  }, []);

  const remainingMs = attempt
    ? Math.max(0, (deadlineMonotonicAt.current ?? now) - now)
    : 0;
  const remainingSeconds = Math.ceil(remainingMs / 1000);
  const timerLabel = `${Math.floor(remainingSeconds / 60)
    .toString()
    .padStart(2, "0")}:${(remainingSeconds % 60).toString().padStart(2, "0")}`;

  useEffect(() => {
    if (
      !attempt ||
      attempt.status !== "IN_PROGRESS" ||
      remainingMs > 0 ||
      !sessionId ||
      autoSubmitting.current
    ) {
      return;
    }
    autoSubmitting.current = true;
    api
      .request(`/attempts/${attempt.attempt_id}/submit`, {
        method: "POST",
        body: {},
        headers: { "X-Exam-Session": sessionId },
      })
      .then(setAttempt)
      .catch((e) => setSaveError(e.message));
  }, [attempt, remainingMs, sessionId]);

  async function requestWithRetry(path, options) {
    let lastError;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        return await api.request(path, options);
      } catch (e) {
        lastError = e;
        const retryable = e.status === 0 || e.status === 429 || e.status >= 500;
        if (!retryable || attempt === 2) throw e;
        await new Promise((resolve) =>
          window.setTimeout(resolve, 250 * 2 ** attempt),
        );
      }
    }
    throw lastError;
  }

  async function saveAnswer(questionId, optionId) {
    if (
      !attempt ||
      attempt.status !== "IN_PROGRESS" ||
      savingAnswers[questionId]
    ) {
      return;
    }
    const question = attempt.questions.find((item) => item.id === questionId);
    const previous = question?.selected_option_id ?? null;
    setSaveError("");
    setSavingAnswers((current) => ({ ...current, [questionId]: true }));
    setAttempt((current) => ({
      ...current,
      questions: current.questions.map((item) =>
        item.id === questionId
          ? { ...item, selected_option_id: optionId }
          : item,
      ),
      answers: { ...current.answers, [questionId]: optionId },
    }));
    try {
      const result = await requestWithRetry(
        `/attempts/${attempt.attempt_id}/answers`,
        {
          method: "PATCH",
          body: { question_id: questionId, option_id: optionId },
          headers: { "X-Exam-Session": sessionId },
        },
      );
      setAttempt((current) => ({ ...current, last_saved_at: result.saved_at }));
    } catch (e) {
      setAttempt((current) => ({
        ...current,
        questions: current.questions.map((item) =>
          item.id === questionId
            ? { ...item, selected_option_id: previous }
            : item,
        ),
        answers: { ...current.answers, [questionId]: previous },
      }));
      setSaveError(`Your answer was not saved: ${e.message}`);
    } finally {
      setSavingAnswers((current) => {
        const next = { ...current };
        delete next[questionId];
        return next;
      });
    }
  }

  async function submitAttempt() {
    if (!attempt || submitting) return;
    setSubmitting(true);
    setSaveError("");
    try {
      const data = await api.request(`/attempts/${attempt.attempt_id}/submit`, {
        method: "POST",
        body: {},
        headers: { "X-Exam-Session": sessionId },
      });
      setAttempt(data);
      setSubmitPending(false);
    } catch (e) {
      setSaveError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <section className="card padded" aria-live="polite" role="status">
        Opening your exam and restoring saved answers…
      </section>
    );
  }
  if (error) {
    return (
      <section className="card padded">
        <div className="section-title">
          <h2>{exam.title}</h2>
          <button className="quiet" onClick={onBack}>
            Back to exams
          </button>
        </div>
        <p className="notice error" role="alert">
          {error}
        </p>
        <button className="secondary" onClick={() => window.location.reload()}>
          Retry this session
        </button>
      </section>
    );
  }
  if (!attempt) return null;

  const isOpen = attempt.status === "IN_PROGRESS";
  return (
    <section className="card padded attempt-shell">
      <div className="section-title attempt-header">
        <div>
          <p className="eyebrow">EXAM IN PROGRESS</p>
          <h1>{attempt.exam_title}</h1>
          <p className="muted">
            Answers save to the server as you choose each option.
          </p>
        </div>
        <div
          className={
            remainingSeconds <= 60 && isOpen ? "timer urgent" : "timer"
          }
        >
          <span>Time remaining</span>
          <strong aria-label={`Time remaining ${timerLabel}`}>
            {isOpen ? timerLabel : "—"}
          </strong>
        </div>
      </div>
      {saveError && (
        <p className="notice error" role="alert">
          {saveError}
        </p>
      )}
      <p className="hint" role="status" aria-live="polite">
        {Object.keys(savingAnswers).length
          ? "Saving answer…"
          : attempt.last_saved_at
            ? `Last saved ${new Date(attempt.last_saved_at).toLocaleTimeString()}`
            : "No answers saved yet."}
      </p>

      {!isOpen ? (
        <div className="notice" role="status">
          {attempt.status === "AUTO_SUBMITTED"
            ? "Time expired. Your attempt was automatically submitted."
            : "Your attempt has been submitted."}
          <p>
            Answer editing is now locked. Evaluation and results will be
            provided in a later release.
          </p>
          <button className="secondary" onClick={onBack}>
            Back to exams
          </button>
        </div>
      ) : (
        <>
          <div className="attempt-progress">
            <strong>
              {attempt.questions.filter((q) => q.selected_option_id).length}
            </strong>
            <span>of {attempt.questions.length} answered</span>
          </div>
          {attempt.questions.map((question, index) => (
            <fieldset
              className="attempt-question"
              key={question.id}
              disabled={!isOpen || !!savingAnswers[question.id]}
            >
              <legend>
                <span>Question {index + 1}</span>
                <small>{question.marks} marks</small>
              </legend>
              <p>{question.text}</p>
              <div className="attempt-options">
                {question.options.map((option) => (
                  <label
                    key={option.id}
                    className={
                      question.selected_option_id === option.id
                        ? "attempt-option selected"
                        : "attempt-option"
                    }
                  >
                    <input
                      type="radio"
                      name={`answer-${question.id}`}
                      value={option.id}
                      checked={question.selected_option_id === option.id}
                      onChange={() => saveAnswer(question.id, option.id)}
                    />
                    <span>{option.text}</span>
                  </label>
                ))}
              </div>
              {question.selected_option_id && (
                <button
                  className="quiet"
                  type="button"
                  onClick={() => saveAnswer(question.id, null)}
                >
                  Clear answer
                </button>
              )}
            </fieldset>
          ))}
          {!submitPending ? (
            <button
              className="primary"
              onClick={() => setSubmitPending(true)}
              disabled={submitting || Object.keys(savingAnswers).length > 0}
            >
              Submit exam
            </button>
          ) : (
            <div
              className="notice"
              role="alertdialog"
              aria-labelledby="submit-confirm-title"
            >
              <strong id="submit-confirm-title">Submit this exam?</strong>
              <p>
                You will not be able to change your answers after submission.
              </p>
              <div className="row-actions">
                <button
                  className="primary"
                  onClick={submitAttempt}
                  disabled={submitting}
                >
                  {submitting ? "Submitting…" : "Confirm submission"}
                </button>
                <button
                  className="secondary"
                  onClick={() => setSubmitPending(false)}
                  disabled={submitting}
                >
                  Keep working
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}

export function AvailableExams() {
  const state = useLoad(() => api.request("/exams/available"));
  const [selectedExam, setSelectedExam] = useState(null);
  if (selectedExam) {
    return (
      <ExamAttemptRunner
        exam={selectedExam}
        onBack={() => {
          setSelectedExam(null);
          state.reload();
        }}
      />
    );
  }
  return (
    <>
      <Heading
        eyebrow="YOUR ASSESSMENTS"
        title="A clear view of what’s ahead."
        description="Exams appear here during their scheduled window when your batch is assigned."
      >
        <button className="secondary" onClick={state.reload}>
          Refresh list
        </button>
      </Heading>
      <LoadState state={state}>
        {state.data && (
          <section className="card">
            <div className="section-title padded">
              <h2>
                Available exams{" "}
                <span className="count">{state.data.results.length}</span>
              </h2>
            </div>
            {!state.data.results.length ? (
              <Empty>
                No exams are available right now. Check back during your
                scheduled exam window.
              </Empty>
            ) : (
              <div className="exam-grid">
                {state.data.results.map((e) => {
                  let saved = null;
                  try {
                    saved = JSON.parse(
                      sessionStorage.getItem(`oep:attempt:${e.exam_id}`) ||
                        "null",
                    );
                  } catch {
                    saved = null;
                  }
                  return (
                    <article className="exam-card" key={e.exam_id}>
                      <span className="badge easy">Assigned to your batch</span>
                      <h3>{e.title}</h3>
                      <p>{e.duration_minutes} minutes</p>
                      <p className="muted">
                        Starts {dateText(e.start_time)}
                        <br />
                        Ends {dateText(e.end_time)}
                      </p>
                      <p className="hint">
                        {saved?.attempt_id
                          ? "A saved attempt exists in this browser session."
                          : "Your answers will be saved as you work."}
                      </p>
                      <button
                        className="primary"
                        onClick={() => setSelectedExam(e)}
                      >
                        {saved?.attempt_id ? "Continue exam" : "Start exam"}
                      </button>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        )}
      </LoadState>
    </>
  );
}
