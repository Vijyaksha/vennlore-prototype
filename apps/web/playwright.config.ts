import { defineConfig } from "@playwright/test";

// E2E targets:
//   PLAYWRIGHT_BASE_URL=https://<deployment> npm run e2e --workspace=web   (a deployed instance)
//   npm run e2e --workspace=web   (starts `next start` on :3000 against DATABASE_URL; CI and local Docker)
const baseURL = process.env.PLAYWRIGHT_BASE_URL;

export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.e2e.ts",
  use: {
    baseURL: baseURL ?? "http://localhost:3000",
    trace: "retain-on-failure",
  },
  reporter: [["list"]],
  webServer: baseURL
    ? undefined
    : {
        command: "npm run start -- --port 3000",
        url: "http://localhost:3000",
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
});
