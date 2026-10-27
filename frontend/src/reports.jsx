import React, { useState } from "react";
import { api } from "./api";
import { ActionNotice, Empty, Heading, LoadState, useAction, useLoad } from "./components";

export function Reports() {
  const [examId, setExamId] = useState("");
  const [kind, setKind] = useState("class");
  const [reason, setReason] = useState("");
  const action = useAction();
  const exams = useLoad(() => api.all("/exams"));
  const report = useLoad(
    () => examId ? api.request(`/admin/reports/${kind}?exam_id=${encodeURIComponent(examId)}`) : Promise.resolve({ results: [] }),
    [examId, kind],
  );
  const attempts = useLoad(
    () => examId ? api.request("/admin/attempts?exam_id=" + encodeURIComponent(examId)) : Promise.resolve({ results: [] }),
    [examId],
  );
  const rows = report.data?.results || [];
  const columns = rows.length ? Object.keys(rows[0]) : [];
  return (
    <>
      <Heading eyebrow="RESULTS" title="Reports" description="Released class results and question-level performance." />
      <ActionNotice action={action} />
      <section className="card padded">
        <label className="field"><span>Exam</span>
          <select value={examId} onChange={(event) => setExamId(event.target.value)}>
            <option value="">Choose an exam</option>
            {(exams.data || []).map((exam) => <option key={exam.id} value={exam.id}>{exam.title}</option>)}
          </select>
        </label>
        <div className="segmented">
          <button className={kind === "class" ? "primary" : "secondary"} onClick={() => setKind("class")}>Class results</button>
          <button className={kind === "questions" ? "primary" : "secondary"} onClick={() => setKind("questions")}>Question analysis</button>
        </div>
      </section>
      {examId && <section className="card">
        <div className="section-title padded">
          <h2>{kind === "class" ? "Class score report" : "Question performance"}</h2>
          <div className="row-actions">
            <button className="secondary" disabled={!rows.length || action.busy} onClick={() => action.run(() => api.download(`/admin/reports/${kind}?exam_id=${encodeURIComponent(examId)}&format=csv`, `${kind}-report.csv`))}>Export CSV</button>
            <button className="secondary" disabled={!rows.length || action.busy} onClick={() => action.run(() => api.download(`/admin/reports/${kind}?exam_id=${encodeURIComponent(examId)}&format=pdf`, `${kind}-report.pdf`))}>Export PDF</button>
          </div>
        </div>
        <LoadState state={report}>
          {!rows.length ? <Empty>No report rows are available yet.</Empty> : <div className="table-wrap"><table>
            <thead><tr>{columns.map((column) => <th key={column}>{column.replaceAll("_", " ")}</th>)}</tr></thead>
            <tbody>{rows.map((row, index) => <tr key={row.student_id || row.question_id || index}>
              {columns.map((column) => <td key={column}>{row[column] ?? "—"}</td>)}
            </tr>)}</tbody>
          </table></div>}
        </LoadState>
      </section>}
      {examId && <section className="card">
        <div className="section-title padded"><h2>Attempt review</h2><button className="quiet" onClick={attempts.reload}>Refresh</button></div>
        <LoadState state={attempts}>
          {!attempts.data?.results?.length ? <Empty>No attempts are recorded for this exam.</Empty> : <div className="table-wrap"><table>
            <thead><tr><th>Student</th><th>Submitted</th><th>Focus events</th><th>Review</th></tr></thead>
            <tbody>{attempts.data.results.map((item) => <tr key={item.attempt_id}>
              <td>{item.student_name}<p className="hint">{item.score ?? "Score hidden"}</p></td>
              <td>{item.submitted_at ? new Date(item.submitted_at).toLocaleString() : "In progress"}</td>
              <td>{item.flags.length ? item.flags.map((flag, index) => <p key={index}>{flag.event_type} · {new Date(flag.occurred_at).toLocaleString()}</p>) : "None recorded"}</td>
              <td>{item.is_disqualified ? <button className="secondary" disabled={action.busy} onClick={() => action.run(async () => {
                await api.request("/admin/attempts/" + item.attempt_id + "/override", { method: "POST", body: { disqualified: false, reason: "" } });
                attempts.reload();
                report.reload();
              }, "Attempt re-permitted.")}>Re-permit</button> : <div>
                <input aria-label={"Review reason for " + item.student_name} placeholder="Reason required" value={reason} onChange={(event) => setReason(event.target.value)} />
                <button className="quiet" disabled={action.busy || !reason.trim()} onClick={() => action.run(async () => {
                  await api.request("/admin/attempts/" + item.attempt_id + "/override", { method: "POST", body: { disqualified: true, reason: reason.trim() } });
                  setReason("");
                  attempts.reload();
                  report.reload();
                }, "Attempt marked for disqualification.")}>Disqualify</button>
              </div>}</td>
            </tr>)}</tbody>
          </table></div>}
        </LoadState>
      </section>}
    </>
  );
}
