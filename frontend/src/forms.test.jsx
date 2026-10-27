import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuestionEditor } from "./questions";
import { api } from "./api";
afterEach(cleanup);
const question = {
  id: "q",
  text: "<script>alert(1)</script>",
  subject: "SE",
  topic: "Testing",
  difficulty: "EASY",
  default_marks: "2.00",
  negative_marks: "0.00",
  options: [
    { text: "A", is_correct: true },
    { text: "B", is_correct: false },
  ],
};
describe("question editor", () => {
  it("rejects duplicate option text before sending", async () => {
    const request = vi.spyOn(api, "request").mockResolvedValue({});
    const user = userEvent.setup();
    render(
      <QuestionEditor
        question={question}
        onSaved={() => {}}
        onCancel={() => {}}
      />,
    );
    await user.clear(screen.getByLabelText("Option 2", { exact: true }));
    await user.type(screen.getByLabelText("Option 2", { exact: true }), "a");
    await user.click(screen.getByRole("button", { name: "Save question" }));
    expect((await screen.findByRole("alert")).textContent).toContain(
      "distinct",
    );
    expect(request).not.toHaveBeenCalled();
  });
  it("uses text values and surfaces server in-use errors", async () => {
    vi.spyOn(api, "request").mockRejectedValue(
      new Error("Question belongs to an exam."),
    );
    const user = userEvent.setup();
    render(
      <QuestionEditor
        question={question}
        onSaved={() => {}}
        onCancel={() => {}}
      />,
    );
    expect(screen.getByLabelText("Question text").value).toBe(question.text);
    expect(document.querySelector("script")).toBe(null);
    await user.click(screen.getByRole("button", { name: "Save question" }));
    expect((await screen.findByRole("alert")).textContent).toContain(
      "belongs to an exam",
    );
  });
  it("allows selecting one correct option and saves the full list", async () => {
    const request = vi.spyOn(api, "request").mockResolvedValue({}),
      saved = vi.fn(),
      user = userEvent.setup();
    render(
      <QuestionEditor
        question={question}
        onSaved={saved}
        onCancel={() => {}}
      />,
    );
    await user.click(
      screen.getByRole("radio", { name: "Option 2 is correct" }),
    );
    await user.click(screen.getByRole("button", { name: "Save question" }));
    expect(saved).toHaveBeenCalledOnce();
    expect(
      request.mock.calls[0][1].body.options.map((o) => o.is_correct),
    ).toEqual([false, true]);
  });
});
