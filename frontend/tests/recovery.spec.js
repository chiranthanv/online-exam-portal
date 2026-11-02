import { chromium, expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const password = "Recovery-Fixture-Password-123!";

function fixture(completed = false) {
  const root = path.resolve(process.cwd(), "..");
  const python =
    process.env.PLAYWRIGHT_PYTHON || path.join(root, ".venv", "bin", "python");
  const bootstrap =
    "import os,runpy,sys; root=sys.argv[1]; sys.path.insert(0,os.path.join(root,'backend')); os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); import django; django.setup(); runpy.run_path(os.path.join(root,'frontend','tests','recovery_fixture.py'),run_name='__main__')";
  const output = execFileSync(python, ["-c", bootstrap, root], {
    encoding: "utf8",
    env: { ...process.env, RECOVERY_FIXTURE_COMPLETED: completed ? "1" : "0" },
  });
  const record = output
    .split("\n")
    .find((line) => line.startsWith("RECOVERY_FIXTURE="));
  if (!record)
    throw new Error("Recovery fixture did not return its isolated record");
  return JSON.parse(record.slice("RECOVERY_FIXTURE=".length));
}

async function signIn(page, email) {
  await page.goto("/");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in →" }).click();
  await expect(
    page.getByRole("navigation", { name: "Main navigation" }),
  ).toBeVisible();
}

test("offline recovery isolates attempts and preserves original local age", async ({
  page,
}) => {
  await page.goto("/");
  const record = await page.evaluate(async () => {
    const m = await import("/src/attempt-recovery.js");
    const savedAt = Date.now() - 65000;
    await m.savePendingAnswers(
      "shared-exam",
      "attempt-A",
      { question: "A" },
      savedAt,
    );
    const other = await m.loadPendingAnswers("shared-exam", "attempt-B");
    const own = await m.loadPendingAnswers("shared-exam", "attempt-A");
    await m.savePendingAnswers("shared-exam", "attempt-B", { question: "B" });
    await m.clearPendingAnswers("shared-exam", "attempt-A");
    const second = await m.loadPendingAnswers("shared-exam", "attempt-B");
    const wrongExam = await m.loadPendingAnswers("different-exam", "attempt-B");
    await m.clearPendingAnswers("shared-exam", "attempt-B");
    return {
      other: other.answers,
      own: own.answers,
      age: own.age_ms,
      timestamp: own.saved_at === savedAt,
      second: second.answers,
      wrongExam: wrongExam.answers,
    };
  });
  expect(record.other).toEqual({});
  expect(record.own).toEqual({ question: "A" });
  expect(record.age).toBeGreaterThanOrEqual(65000);
  expect(record.timestamp).toBe(true);
  expect(record.second).toEqual({ question: "B" });
  expect(record.wrongExam).toEqual({});
});

test("committed offline answers recover after renderer crash and browser restart", async ({
  browserName,
}, testInfo) => {
  test.skip(browserName !== "chromium", "Renderer crash uses Chromium CDP");
  test.setTimeout(90000);
  const data = fixture();
  const profile = await mkdtemp(path.join(tmpdir(), "oep-recovery-"));
  let context;
  try {
    context = await chromium.launchPersistentContext(profile, {
      ...testInfo.project.use.launchOptions,
      headless: true,
      baseURL: testInfo.project.use.baseURL,
    });
    const page = await context.newPage();
    await signIn(page, data.email);
    await page.route(/\/api\/v1\/attempts\/[^/]+\/answers$/, async (route) => {
      if (route.request().method() !== "PATCH") return route.continue();
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Synthetic outage" }),
      });
    });
    const [start] = await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().endsWith(`/exams/${data.exam_id}/attempt`) &&
          response.request().method() === "POST",
      ),
      page.getByRole("button", { name: "Start exam", exact: true }).click(),
    ]);
    const attempt = await start.json();
    await page
      .locator("fieldset.attempt-question")
      .first()
      .getByRole("radio")
      .first()
      .check();
    await expect(
      page.locator(".attempt-save-status [role='status']"),
    ).toContainText("waiting to sync");
    await expect
      .poll(() =>
        page.evaluate(
          async ({ examId, attemptId }) => {
            const m = await import("/src/attempt-recovery.js");
            return Object.keys(
              (await m.loadPendingAnswers(examId, attemptId)).answers,
            ).length;
          },
          { examId: data.exam_id, attemptId: attempt.attempt_id },
        ),
      )
      .toBe(1);
    const cookie = (await context.cookies()).find((item) =>
      item.name.startsWith("oep_attempt_session_"),
    );
    expect(cookie?.httpOnly).toBe(true);
    const storage = await page.evaluate(() =>
      JSON.stringify({
        session: Object.entries(sessionStorage),
        local: Object.entries(localStorage),
      }),
    );
    expect(storage).not.toContain("session_id");
    expect(storage).not.toContain("access_token");
    const cdp = await context.newCDPSession(page);
    const crashed = page.waitForEvent("crash", { timeout: 10000 });
    // Page.crash may never return a protocol reply after its renderer exits.
    const crashRequest = cdp.send("Page.crash").catch(() => {});
    await crashed;
    await context.close();
    await crashRequest;
    context = await chromium.launchPersistentContext(profile, {
      ...testInfo.project.use.launchOptions,
      headless: true,
      baseURL: testInfo.project.use.baseURL,
    });
    const resumed = await context.newPage();
    await resumed.goto("/");
    await expect(
      resumed.getByRole("navigation", { name: "Main navigation" }),
    ).toBeVisible();
    await resumed
      .getByRole("button", { name: "Start exam", exact: true })
      .click();
    await expect(
      resumed
        .locator("fieldset.attempt-question")
        .first()
        .getByRole("radio")
        .first(),
    ).toBeChecked();
    await expect(
      resumed.getByText(/Recovered 1 unsynced answer/),
    ).toBeVisible();
    await expect(
      resumed.locator(".attempt-save-status [role='status']"),
    ).toContainText("Last saved", { timeout: 15000 });
    await resumed
      .getByRole("button", { name: "Submit exam", exact: true })
      .click();
    await resumed
      .getByRole("button", { name: "Confirm submission", exact: true })
      .click();
    await expect(
      resumed.getByRole("status").filter({ hasText: "Attempt submitted" }),
    ).toBeVisible();
  } finally {
    await context?.close().catch(() => {});
    if (profile.startsWith(path.join(tmpdir(), "oep-recovery-"))) {
      await rm(profile, { recursive: true, force: true });
    }
  }
});

test("student can find released results after the exam window has ended", async ({
  page,
}) => {
  const data = fixture(true);
  await signIn(page, data.email);
  await expect(
    page.getByText("No exams are available right now.", { exact: false }),
  ).toBeVisible();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("button", { name: /Results/ })
    .click();
  const card = page.locator("article").filter({ hasText: data.title });
  await expect(card.getByRole("heading", { name: data.title })).toBeVisible();
  await expect(card.getByText("Released", { exact: true })).toBeVisible();
  await expect(card).toContainText(`Score: ${data.score} / ${data.score}`);
});
