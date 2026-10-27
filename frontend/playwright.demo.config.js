import base from "./playwright.config.js";
import { defineConfig } from "@playwright/test";
export default defineConfig({
  ...base,
  testDir: "./demo",
  outputDir: "./demo-results",
  timeout: 100000,
  reporter: "list",
  use: {
    ...base.use,
    viewport: { width: 1280, height: 900 },
    video: { mode: "on", size: { width: 1280, height: 900 } },
    trace: "off",
  },
});
