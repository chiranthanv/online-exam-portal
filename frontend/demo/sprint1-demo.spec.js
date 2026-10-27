import { test, expect } from "@playwright/test";
test("one-minute actual Sprint 1 product demonstration", async ({
  page,
}, testInfo) => {
  const started = Date.now();
  async function holdUntil(seconds) {
    const remaining = seconds * 1000 - (Date.now() - started);
    if (remaining > 0) await page.waitForTimeout(remaining);
  }
  async function signIn(role) {
    await page.goto("/");
    await page.getByLabel("Email address").fill(`demo-${role}@example.test`);
    await page
      .getByLabel("Password", { exact: true })
      .fill("Local-Demo-Only-827!");
    await page.getByRole("button", { name: "Sign in →" }).click();
    await expect(
      page.getByRole("navigation", { name: "Main navigation" }),
    ).toBeVisible();
  }
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Sign in to your workspace" }),
  ).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("01-sign-in.png") });
  await holdUntil(3);
  await signIn("admin");
  await page.screenshot({ path: testInfo.outputPath("02-exams.png") });
  await holdUntil(8);
  await page.getByRole("button", { name: "02 Question bank" }).click();
  await page.getByRole("button", { name: "+ New question" }).click();
  await page
    .getByLabel("Question text")
    .fill("Which test verifies several modules working together?");
  await page
    .getByLabel("Subject", { exact: true })
    .fill("Software Engineering");
  await page.getByLabel("Topic", { exact: true }).fill("Integration");
  await page
    .getByLabel("Option 1", { exact: true })
    .fill("Integration testing");
  await page.getByLabel("Option 2", { exact: true }).fill("A syntax check");
  await holdUntil(15);
  await page.getByRole("button", { name: "Save question" }).click();
  await expect(
    page.getByText("Question saved.", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("Filter by topic").fill("Integration");
  await page.getByRole("button", { name: "Apply filters" }).click();
  await page.screenshot({ path: testInfo.outputPath("03-question-bank.png") });
  await holdUntil(21);
  await page.getByRole("button", { name: "03 Students & batches" }).click();
  await page.getByLabel("Roster file").setInputFiles({
    name: "demo-roster.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(
      `name,email,usn,batch\nDemo Import,recording${Date.now()}@example.test,R${Date.now()},DEMO-CSE-A\nInvalid,bad-email,INVALID,DEMO-CSE-A\n`,
    ),
  });
  await page
    .getByRole("button", { name: "Import roster", exact: true })
    .click();
  await expect(
    page.getByText("1 student imported. 1 row rejected.", { exact: true }),
  ).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("04-import-errors.png") });
  await holdUntil(31);
  await page.getByRole("button", { name: "01 Exams" }).click();
  await page.getByRole("button", { name: "+ Create exam" }).click();
  const title = "Software Engineering · Quiz 1";
  await page.getByLabel("Exam title").fill(title);
  const value = (delta) => {
    const d = new Date(Date.now() + delta);
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
  };
  await page.getByLabel("Starts at").fill(value(3600000));
  await page.getByLabel("Ends at").fill(value(7200000));
  await page.getByLabel("Results visible from").fill(value(10800000));
  await holdUntil(36);
  await page.getByRole("button", { name: "Save schedule" }).click();
  const card = page.locator("article").filter({ hasText: title });
  await card.getByRole("button", { name: "Configure exam" }).click();
  const config = page.locator(".configuration");
  await config.getByRole("radio", { name: "Random selection" }).check();
  await config.getByLabel("Number of questions").fill("5");
  await config.getByRole("button", { name: "Select random questions" }).click();
  await expect(
    page.getByText("Random question selection and total marks saved.", {
      exact: true,
    }),
  ).toBeVisible();
  await config
    .locator(".checkbox-list label")
    .filter({ hasText: "DEMO-CSE-A" })
    .getByRole("checkbox")
    .check();
  await config.getByRole("button", { name: "Save batch assignments" }).click();
  await expect(
    page.getByText("Batch assignments saved.", { exact: true }),
  ).toBeVisible();
  await config.getByRole("button", { name: "Close", exact: true }).click();
  await page.screenshot({ path: testInfo.outputPath("05-scheduled-exam.png") });
  await holdUntil(49);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await signIn("student");
  await expect(
    page.getByRole("heading", { name: "[DEMO] Available practice exam" }),
  ).toBeVisible();
  await page.screenshot({
    path: testInfo.outputPath("06-student-eligibility.png"),
  });
  await holdUntil(60);
});
