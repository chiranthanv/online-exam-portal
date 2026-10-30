// Run only against an isolated local demo database. No forms or exams are submitted.
/* global process, URL, fetch, document, window, getComputedStyle, innerWidth, innerHeight, console */
import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";
import puppeteer from "puppeteer-core";
import { startFlow } from "lighthouse";

const base = process.env.AUDIT_URL || "http://127.0.0.1:5173";
const target = new URL(base);
if (!["localhost", "127.0.0.1"].includes(target.hostname)) {
  throw new Error("Only local disposable demo environments are supported.");
}
if (process.env.AUDIT_DISPOSABLE !== "1") {
  throw new Error(
    "Set AUDIT_DISPOSABLE=1 after preparing a fresh local demo database.",
  );
}
const out = path.resolve(process.env.AUDIT_OUTPUT || "accessibility-results");
await fs.mkdir(out, { recursive: true });
// Refuse to replace a previous run's measurements.
try {
  await fs.access(path.join(out, "COMPLETED"));
  throw new Error(
    "This evidence directory already contains a completed audit.",
  );
} catch (error) {
  if (error.code !== "ENOENT") throw error;
}
const reservation = await fs.open(path.join(out, "RUNNING"), "wx");
await reservation.close();
const report = {
  startedAt: new Date().toISOString(),
  commit: execFileSync("git", ["rev-parse", "HEAD"], {
    encoding: "utf8",
  }).trim(),
  node: process.version,
  base,
  findings: [],
};
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
try {
  report.browser = await browser.version();
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto(base, { waitUntil: "networkidle0" });
  // API authentication avoids submitting a login form; only synthetic seeded data is used.
  await page.evaluate(async () => {
    const csrf = await (await fetch("/api/v1/auth/csrf")).json();
    const response = await fetch("/api/v1/auth/login", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf.csrf_token,
      },
      body: JSON.stringify({
        email: "demo-student@example.test",
        password: "Local-Demo-Only-827!",
      }),
    });
    if (!response.ok) throw new Error(`Demo login failed: ${response.status}`);
  });
  await page.reload({ waitUntil: "networkidle0" });
  await page.waitForSelector(".exam-card");
  await page.evaluate(() => document.activeElement?.blur());
  await page.keyboard.press("Tab");
  report.findings.push({
    check: "Skip link first in keyboard order",
    passed: await page.evaluate(
      () => document.activeElement?.textContent === "Skip to main content",
    ),
  });
  await page.keyboard.press("Enter");
  report.findings.push({
    check: "Skip link moves focus to main",
    passed: await page.evaluate(
      () => document.activeElement?.tagName === "MAIN",
    ),
  });
  const start = await page.waitForSelector("::-p-text(Start exam)");
  await start.click();
  await page.waitForSelector(".attempt-question");
  // Do not select answers or confirm submission. This audit observes the open fixture.
  report.questions = await page.$$eval(
    ".attempt-question",
    (nodes) => nodes.length,
  );
  report.findings.push({
    check: "Every answer radio has a label and question group",
    passed: await page.$$eval(
      ".attempt-question input[type=radio]",
      (nodes) =>
        nodes.length > 0 &&
        nodes.every(
          (e) =>
            e.labels.length > 0 &&
            e.labels[0].textContent.trim().length > 0 &&
            e.closest("fieldset")?.querySelector("legend")?.textContent.trim()
              .length > 0,
        ),
    ),
  });
  await page.evaluate(() => {
    document.activeElement?.blur();
    window.scrollTo(0, 0);
  });
  await page.keyboard.press("Tab");
  // Inspect focus after actual keyboard navigation, rather than calling element.focus().
  report.keyboardFocus = await page.evaluate(() => {
    const e = document.activeElement,
      s = getComputedStyle(e);
    return {
      tag: e.tagName,
      text: e.textContent.trim().slice(0, 80),
      outline: s.outline,
      outlineOffset: s.outlineOffset,
    };
  });
  for (const width of [1440, 390, 320]) {
    await page.setViewport({ width, height: width === 1440 ? 900 : 844 });
    await page.evaluate(() => window.scrollTo(0, 0));
    const flow = await startFlow(page, {
      name: `Authenticated open exam at ${width}px`,
      config: {
        extends: "lighthouse:default",
        settings: {
          onlyCategories: ["accessibility"],
          screenEmulation: { disabled: true },
          formFactor: width === 1440 ? "desktop" : "mobile",
        },
      },
    });
    await flow.snapshot({ name: `Open attempt ${width}px` });
    const result = await flow.createFlowResult();
    const lhr = result.steps[0].lhr;
    await fs.writeFile(
      path.join(out, `lighthouse-${width}.json`),
      JSON.stringify(lhr, null, 2),
    );
    report.findings.push({
      check: `Lighthouse accessibility >=90 at ${width}px`,
      passed: lhr.categories.accessibility.score >= 0.9,
      score: lhr.categories.accessibility.score * 100,
      failures: Object.values(lhr.audits)
        .filter((a) => a.score === 0)
        .map((a) => ({ id: a.id, title: a.title })),
    });
    report.findings.push({
      check: `No automated WCAG 2.0/2.1 AA failures at ${width}px`,
      passed: !Object.values(lhr.audits).some(
        (a) =>
          a.score === 0 &&
          a.details?.debugData?.tags?.some((tag) =>
            ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"].includes(tag),
          ),
      ),
    });
    report.findings.push({
      check: `No horizontal page overflow at ${width}px`,
      ...(await page.evaluate(() => ({
        passed: document.documentElement.scrollWidth <= innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        viewport: innerWidth,
      }))),
    });
    await page.screenshot({ path: path.join(out, `exam-top-${width}.png`) });
    await page.evaluate(() =>
      window.scrollTo(0, document.documentElement.scrollHeight),
    );
    const timer = await page.$eval(".timer", (e) => {
      const r = e.getBoundingClientRect();
      return {
        passed: r.top >= 0 && r.bottom <= innerHeight,
        top: r.top,
        bottom: r.bottom,
        viewportHeight: innerHeight,
      };
    });
    report.findings.push({
      check: `Timer stays visible at page bottom ${width}px`,
      ...timer,
    });
    await page.screenshot({ path: path.join(out, `exam-bottom-${width}.png`) });
  }
  report.completedAt = new Date().toISOString();
  await fs.writeFile(
    path.join(out, "summary.json"),
    JSON.stringify(report, null, 2),
  );
  await fs.rename(path.join(out, "RUNNING"), path.join(out, "COMPLETED"));
  console.log(JSON.stringify(report, null, 2));
  if (report.findings.some((f) => !f.passed)) process.exitCode = 1;
} finally {
  await browser.close();
}
