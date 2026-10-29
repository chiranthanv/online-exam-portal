// Use the real built SPA and Chromium while the independent 200-student load is running.
import fs from "node:fs";
import { performance } from "node:perf_hooks";
import { createRequire } from "node:module";
const require = createRequire(new URL("../../frontend/package.json", import.meta.url));
const { chromium } = require("@playwright/test");
const [manifestPath, baseURL, output] = process.argv.slice(2);
const url = new URL(baseURL);
if (url.protocol !== "http:" || !["localhost", "127.0.0.1"].includes(url.hostname)) {
  throw new Error("Disposable loopback URLs only");
}
const manifest = JSON.parse(fs.readFileSync(manifestPath));
const browser = await chromium.launch({ headless: true });
const samples = [];
try {
  for (const account of manifest.browser_accounts) {
    const context = await browser.newContext(); // cold browser context, no cached credentials/assets
    const page = await context.newPage();
    const failures = [];
    page.on("pageerror", (e) => failures.push(e.message));
    try {
      await page.goto(baseURL);
      await page.getByLabel("Email address").fill(account.email);
      await page.getByLabel("Password", { exact: true }).fill(account.password);
      await page.getByRole("button", { name: "Sign in →" }).click();
      const card = page.locator("article").filter({ hasText: "[PERF] Current class" });
      const start = card.getByRole("button", { name: "Start exam", exact: true });
      await start.waitFor();
      const began = performance.now();
      await start.click();
      await page.locator(".attempt-question").last().waitFor();
      await page.waitForFunction(() => document.querySelectorAll(".attempt-question").length === 50);
      const seconds = (performance.now() - began) / 1000;
      const count = await page.locator(".attempt-question").count();
      samples.push({ seconds, question_count: count, errors: failures, ok: seconds < 2 && count === 50 && failures.length === 0 });
    } catch (e) {
      samples.push({ ok: false, error: e.message, errors: failures });
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
  fs.writeFileSync(output, JSON.stringify({
    measured_at_utc: new Date().toISOString(),
    definition: "Start exam click to all 50 question fieldsets rendered in real SPA; login and initial shell navigation excluded",
    environment: "headless Chromium, desktop, loopback, no network/CPU throttling, no video",
    samples, page_target_met: samples.length === 5 && samples.every((s) => s.ok),
  }, null, 2));
}
if (samples.length !== 5 || samples.some((s) => !s.ok)) process.exitCode = 1;
