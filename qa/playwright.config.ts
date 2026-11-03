import { defineConfig, devices } from "@playwright/test";

import { qaConfig } from "./automation/framework/config";

const isCi = Boolean(process.env.CI);

export default defineConfig({
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  forbidOnly: isCi,
  retries: isCi ? 1 : 0,
  workers: isCi ? 2 : undefined,
  reporter: [
    ["list"],
    ["html", { outputFolder: "reports/playwright", open: "never" }],
    ["junit", { outputFile: "reports/junit.xml" }],
    ["allure-playwright", { resultsDir: "reports/allure-results" }],
  ],
  outputDir: "reports/test-results",
  use: {
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "api",
      testDir: "./automation/api",
    },
    {
      name: "data",
      testDir: "./automation/data",
    },
    {
      name: "a11y",
      testDir: "./automation/accessibility",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: qaConfig.baseUrl,
      },
    },
    {
      name: "security",
      testDir: "./automation/security",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: qaConfig.baseUrl,
      },
    },
    {
      name: "e2e-chromium",
      testDir: "./automation/e2e",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: qaConfig.baseUrl,
      },
    },
    ...(process.env.QA_BROWSERS === "full"
      ? [
          {
            name: "e2e-firefox",
            testDir: "./automation/e2e",
            use: { ...devices["Desktop Firefox"], baseURL: qaConfig.baseUrl },
          },
          {
            name: "e2e-webkit",
            testDir: "./automation/e2e",
            use: { ...devices["Desktop Safari"], baseURL: qaConfig.baseUrl },
          },
        ]
      : []),
  ],
});
