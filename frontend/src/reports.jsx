import React, { useEffect, useState } from "react";
import { api } from "./api";

export function Reports() {
  const [exams, setExams] = useState([]);
  const [examId, setExamId] = useState("");
  const [attempts, setAttempts] = useState([]);
  const [classRows, setClassRows] = useState([]);
  const [questionRows, setQuestionRows] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadAttempts() {
    const data = await api.request(
      "/admin/attempts" + (examId ? "?exam_id=" + examId : ""),
    );
    setAttempts(data.results || []);
  }

  async function loadReports(id) {
    if (!id) return;
    const [classData, questionData] = await Promise.all([
      api.request("/reports/class?exam_id=" + id),
      api.request("/reports/questions?exam_id=" + id),
    ]);
    setClassRows(classData.results || []);
    setQuestionRows(questionData.results || []);
  }

  useEffect(() => {
    api
      .all("/exams")
      .then((data) => {
        setExams(data);
        if (data.length) setExamId(String(data[0].id));
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!examId) return;
    setError("");
    loadAttempts().catch((e) => setError(e.message));
    loadReports(examId).catch((e) => {
      setClassRows([]);
      setQuestionRows([]);
      setError(e.message);
    });
  }, [examId]);

  async function overrideAttempt(attempt, disqualified) {
    const reason = disqualified
      ? window.prompt("Reason for disqualification (required):")
      : "";
    if (disqualified && !reason?.trim()) return;
    setBusy(true);
    setError("");
    try {
      await api.request("/admin/attempts/" + attempt.attempt_id + "/override", {
        method: "POST",
        body: { disqualified, reason: reason || "" },
      });
      await loadAttempts();
      await loadReports(examId);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">ASSESSMENT OVERSIGHT</p>
        <h1>Reports & attempt review</h1>
        <p className="muted">
          Scores are available only after the exam's configured result-release
          time.
        </p>
      </header>
      {error && (
        <p className="notice error" role="alert">
          {error}
        </p>
      )}
      <section className="card padded">
        <label htmlFor="report-exam">Exam</label>
        <select
          id="report-exam"
          value={examId}
          onChange={(e) => setExamId(e.target.value)}
        >
          {exams.map((exam) => (
            <option key={exam.id} value={exam.id}>
              {exam.title}
            </option>
          ))}
        </select>
        <div className="row-actions">
          <button
            className="secondary"
            disabled={!examId}
            onClick={() =>
              api
                .download(
                  "/reports/class?exam_id=" + examId + "&export=csv",
                  "class-report.csv",
                )
                .catch((e) => setError(e.message))
            }
          >
            Class CSV
          </button>
          <button
            className="secondary"
            disabled={!examId}
            onClick={() =>
              api
                .download(
                  "/reports/class?exam_id=" + examId + "&export=pdf",
                  "class-report.pdf",
                )
                .catch((e) => setError(e.message))
            }
          >
            Class PDF
          </button>
          <button
            className="secondary"
            disabled={!examId}
            onClick={() =>
              api
                .download(
                  "/reports/questions?exam_id=" + examId + "&export=csv",
                  "question-report.csv",
                )
                .catch((e) => setError(e.message))
            }
          >
            Question CSV
          </button>
          <button
            className="secondary"
            disabled={!examId}
            onClick={() =>
              api
                .download(
                  "/reports/questions?exam_id=" + examId + "&export=pdf",
                  "question-report.pdf",
                )
                .catch((e) => setError(e.message))
            }
          >
            Question PDF
          </button>
        </div>
      </section>
      <section className="card padded">
        <h2>Class results</h2>
        {!classRows.length ? (
          <p className="muted">
            No released, evaluated and permitted submissions yet.
          </p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>USN</th>
                  <th>Score</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {classRows.map((row) => (
                  <tr key={row.attempt_id}>
                    <td>{row.student_name}</td>
                    <td>{row.usn}</td>
                    <td>{row.score}</td>
                    <td>{row.total_marks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="card padded">
        <h2>Question analysis</h2>
        {!questionRows.length ? (
          <p className="muted">
            Question analysis appears after result release.
          </p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Question</th>
                  <th>Difficulty</th>
                  <th>Correct</th>
                  <th>Incorrect</th>
                  <th>Unanswered</th>
                </tr>
              </thead>
              <tbody>
                {questionRows.map((row) => (
                  <tr key={row.question_id}>
                    <td>
                      {row.subject} · {row.topic}
                    </td>
                    <td>{row.difficulty}</td>
                    <td>{row.correct}</td>
                    <td>{row.incorrect}</td>
                    <td>{row.unanswered}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="card padded">
        <div className="section-title">
          <h2>Attempt review & proctoring flags</h2>
          <button
            className="quiet"
            disabled={busy}
            onClick={() => loadAttempts().catch((e) => setError(e.message))}
          >
            Refresh
          </button>
        </div>
        {!attempts.length ? (
          <p className="muted">No attempts for this exam.</p>
        ) : (
          attempts.map((attempt) => (
            <article className="attempt-review" key={attempt.attempt_id}>
              <div className="section-title">
                <strong>{attempt.student_name}</strong>
                <span className="badge">{attempt.status}</span>
              </div>
              <p className="hint">
                Attempt {attempt.attempt_id} · Score{" "}
                {attempt.score ?? "Pending"}
              </p>
              <p className="hint">
                {attempt.flags.length} client-reported focus/visibility
                signal(s). These are review signals, not proof of misconduct.
              </p>
              {attempt.flags.map((flag, index) => (
                <p className="hint" key={index}>
                  {flag.event_type} ·{" "}
                  {new Date(flag.occurred_at).toLocaleString()}
                </p>
              ))}
              {attempt.status === "DISQUALIFIED" ? (
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() => overrideAttempt(attempt, false)}
                >
                  Re-permit result
                </button>
              ) : ["SUBMITTED", "AUTO_SUBMITTED"].includes(attempt.status) ? (
                <button
                  className="quiet"
                  disabled={busy}
                  onClick={() => overrideAttempt(attempt, true)}
                >
                  Disqualify attempt
                </button>
              ) : null}
            </article>
          ))
        )}
      </section>
    </>
  );
}
