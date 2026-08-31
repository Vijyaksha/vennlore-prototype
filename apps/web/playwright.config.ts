import { defineConfig } from "@playwright/test";

// E2E runs against a deployed Kindred instance:
//   PLAYWRIGHT_BASE_URL=https://<deployment> npm run e2e --workspace=web
// Without the env var it targets a locally running `next dev` on :3000.
export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.e2e.ts",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
  },
  reporter: [["list"]],
});
