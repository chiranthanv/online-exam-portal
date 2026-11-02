import React from "react";
import { api } from "./api";
import { Empty, Heading, LoadState, dateText, useLoad } from "./components";

const statusText = {
  withheld: "Withheld by an administrator",
  evaluating: "Evaluation pending",
  pending_release: "Waiting for scheduled release",
  released: "Released",
};

export function StudentResults() {
  const state = useLoad(() => api.all("/attempts/results"));
  return (
    <>
      <Heading
        eyebrow="YOUR RESULTS"
        title="Your completed assessments."
        description="Find your results here after an exam ends. Scores appear only after their scheduled release."
      >
        <button className="secondary" onClick={state.reload}>
          Refresh results
        </button>
      </Heading>
      <LoadState state={state}>
        {state.data &&
          (!state.data.length ? (
            <Empty>No completed assessments yet.</Empty>
          ) : (
            <div className="exam-grid">
              {state.data.map((result) => (
                <article className="exam-card" key={result.attempt_id}>
                  <h2>{result.exam_title}</h2>
                  <p>{statusText[result.availability]}</p>
                  <p className="muted">
                    Submitted {dateText(result.submitted_at)}
                  </p>
                  {result.availability === "released" ? (
                    <p>
                      Score: <strong>{result.score}</strong> /{" "}
                      {result.total_marks}
                    </p>
                  ) : result.availability === "pending_release" ? (
                    <p>
                      Scheduled release: {dateText(result.result_visible_from)}
                    </p>
                  ) : null}
                </article>
              ))}
            </div>
          ))}
      </LoadState>
    </>
  );
}
