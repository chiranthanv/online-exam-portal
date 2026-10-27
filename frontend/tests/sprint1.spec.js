import { test, expect } from "@playwright/test";
const password = "Local-Demo-Only-827!";
async function login(page, who = "admin") {
  await page.goto("/");
  await page.getByLabel("Email address").fill(`demo-${who}@example.test`);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in →" }).click();
  await expect(
    page.getByRole("navigation", { name: "Main navigation" }),
  ).toBeVisible();
}
test("admin CRUD, stored XSS stays text, filters and session recovery", async ({
  page,
}) => {
  await login(page);
  await page.getByRole("button", { name: "02 Question bank" }).click();
  await page.getByRole("button", { name: "+ New question" }).click();
  const text = '<img src=x onerror="window.__xss=true"> Browser test question';
  await page.getByLabel("Question text").fill(text);
  await page.getByLabel("Subject", { exact: true }).fill("BrowserTest");
  await page.getByLabel("Topic", { exact: true }).fill("Security");
  await page.getByLabel("Option 1", { exact: true }).fill("Correct");
  await page.getByLabel("Option 2", { exact: true }).fill("Incorrect");
  await page.getByRole("button", { name: "Save question" }).click();
  await expect(
    page.getByText("Question saved.", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("Filter by subject").fill("BrowserTest");
  await page.getByRole("button", { name: "Apply filters" }).click();
  await expect(
    page.getByRole("cell", { name: text, exact: true }),
  ).toBeVisible();
  expect(await page.evaluate(() => window.__xss)).toBeUndefined();
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page.getByLabel("Question text").fill("Browser test revised");
  await page.getByRole("button", { name: "Save question" }).click();
  await expect(
    page.getByRole("cell", { name: "Browser test revised", exact: true }),
  ).toBeVisible();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(
    page.getByText("Question deleted.", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Make room for good exams." }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
    })),
  ).toEqual({ local: 0, session: 0 });
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Sign in to your workspace" }),
  ).toBeVisible();
});
test("partial roster import reports exact errors and memberships are editable", async ({
  page,
}) => {
  await login(page);
  await page.getByRole("button", { name: "03 Students & batches" }).click();
  const suffix = Date.now();
  const batch = `BROWSER-${suffix}`;
  await page.getByLabel("Batch name", { exact: true }).fill(batch);
  await page.getByRole("button", { name: "Create batch", exact: true }).click();
  await expect(page.getByText("Batch created.", { exact: true })).toBeVisible();
  const csv = `name,email,usn,batch\nBrowser Student,browser${suffix}@example.test,B${suffix},${batch}\nInvalid,bad-email,INVALID,${batch}\n`;
  await page.getByLabel("Roster file").setInputFiles({
    name: "roster.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(csv),
  });
  await page
    .getByRole("button", { name: "Import roster", exact: true })
    .click();
  await expect(
    page.getByText("1 student imported. 1 row rejected.", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("list", { name: "Import row errors" }),
  ).toContainText("Row 3:");
  await page.getByRole("button", { name: new RegExp(batch) }).click();
  const other = page
    .locator(".checkbox-list label")
    .filter({ hasText: "Demo Other" })
    .getByRole("checkbox");
  await other.check();
  await page.getByRole("button", { name: "Add selected students (1)" }).click();
  await expect(
    page.getByText("Memberships saved.", { exact: true }),
  ).toBeVisible();
});
test("exam schedule, manual order, random selection and batch assignment persist", async ({
  page,
}) => {
  await login(page);
  await page.getByRole("button", { name: "+ Create exam" }).click();
  const title = `Browser Exam ${Date.now()}`;
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
  await page.getByRole("button", { name: "Save schedule" }).click();
  const card = page.locator("article").filter({ hasText: title });
  await card.getByRole("button", { name: "Configure exam" }).click();
  const config = page.locator(".configuration");
  await config.locator(".questions-picker input").nth(0).check();
  await config.locator(".questions-picker input").nth(1).check();
  await config.getByRole("button", { name: "Move question 2 up" }).click();
  await config.getByRole("button", { name: "Save question selection" }).click();
  await expect(
    page.getByText("Question selection and total marks saved.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(card).toContainText("4.00");
  await config.getByRole("radio", { name: "Random selection" }).check();
  await config.getByLabel("Number of questions").fill("3");
  await config.getByLabel("Use an exact difficulty mix").check();
  await config.getByLabel("EASY count").fill("1");
  await config.getByLabel("MEDIUM count").fill("1");
  await config.getByLabel("HARD count").fill("1");
  await config.getByRole("button", { name: "Select random questions" }).click();
  await expect(
    page.getByText("Random question selection and total marks saved.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(card).toContainText("6.00");
  await config
    .locator(".checkbox-list label")
    .filter({ hasText: "DEMO-CSE-A" })
    .getByRole("checkbox")
    .check();
  await config.getByRole("button", { name: "Save batch assignments" }).click();
  await expect(
    page.getByText("Batch assignments saved.", { exact: true }),
  ).toBeVisible();
  await expect(card).toContainText("1 assigned batch");
});
test("students see eligible exams only; API rejects admin access; mobile layout", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, "student");
  await expect(
    page.getByRole("heading", { name: "[DEMO] Available practice exam" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Question bank" })).toHaveCount(
    0,
  );
  const denial = await page.evaluate(async () => {
    const c = await (
      await fetch("/api/v1/auth/csrf", { credentials: "include" })
    ).json();
    const r = await (
      await fetch("/api/v1/auth/refresh", {
        method: "POST",
        credentials: "include",
        headers: { "X-CSRFToken": c.csrf_token },
      })
    ).json();
    const forbidden = await fetch("/api/v1/questions", {
      headers: { Authorization: `Bearer ${r.access_token}` },
    });
    const list = await (
      await fetch("/api/v1/exams/available", {
        headers: { Authorization: `Bearer ${r.access_token}` },
      })
    ).json();
    return {
      status: forbidden.status,
      keys: JSON.stringify(list).includes("is_correct"),
    };
  });
  expect(denial).toEqual({ status: 403, keys: false });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "other");
  await expect(
    page.getByText("No exams are available right now.", { exact: false }),
  ).toBeVisible();
});

test("email reset is usable once and lockout appears in the browser", async ({
  page,
}) => {
  const { readdir, readFile } = await import("node:fs/promises");
  await login(page);
  await page.getByRole("button", { name: "03 Students & batches" }).click();
  const suffix = Date.now(),
    email = `reset${suffix}@example.test`;
  await page
    .getByLabel("Roster file")
    .setInputFiles({
      name: "reset-fixture.csv",
      mimeType: "text/csv",
      buffer: Buffer.from(
        `name,email,usn,batch\nReset Browser,${email},R${suffix},DEMO-CSE-A\n`,
      ),
    });
  await page
    .getByRole("button", { name: "Import roster", exact: true })
    .click();
  await expect(
    page.getByText("1 student imported. 0 rows rejected.", { exact: true }),
  ).toBeVisible();
  page.once("dialog", (dialog) => dialog.accept());
  await page
    .getByRole("row")
    .filter({ hasText: email })
    .getByRole("button", { name: "Send reset email" })
    .click();
  await expect(
    page.getByText(
      "Password-reset email sent. The link is valid for one hour.",
      { exact: true },
    ),
  ).toBeVisible();
  let token;
  for (const file of await readdir("../backend/.dev-emails")) {
    const message = await readFile(`../backend/.dev-emails/${file}`, "utf8");
    if (message.includes(email))
      token = message.match(/token=([A-Za-z0-9_-]+)/)?.[1];
  }
  expect(Boolean(token)).toBe(true);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await page.goto(`/reset-password?token=${token}`);
  await expect(page).toHaveURL(/\/reset-password$/);
  const newPassword = "Browser-Reset-Passphrase-924!";
  await page.getByLabel("New password", { exact: true }).fill(newPassword);
  await page.getByLabel("Confirm password", { exact: true }).fill(newPassword);
  await page.getByRole("button", { name: "Set password", exact: true }).click();
  await expect(
    page.getByText("Password updated. You can now sign in.", { exact: true }),
  ).toBeVisible();
  await page.goto(`/reset-password?token=${token}`);
  await page.getByLabel("New password", { exact: true }).fill(newPassword);
  await page.getByLabel("Confirm password", { exact: true }).fill(newPassword);
  await page.getByRole("button", { name: "Set password", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Invalid or expired reset link",
  );
  await page.goto("/");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(newPassword);
  await page.getByRole("button", { name: "Sign in →" }).click();
  await expect(
    page.getByRole("heading", { name: "[DEMO] Available practice exam" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill("wrong-password");
  for (let i = 0; i < 5; i++) {
    const response = page.waitForResponse(
      (r) => r.url().endsWith("/auth/login") && r.request().method() === "POST",
    );
    await page.getByRole("button", { name: "Sign in →" }).click();
    expect((await response).status()).toBe(401);
    await expect(page.getByRole("button", { name: "Sign in →" })).toBeEnabled();
  }
  await page.getByLabel("Password", { exact: true }).fill(newPassword);
  await page.getByRole("button", { name: "Sign in →" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Account temporarily locked",
  );
});
