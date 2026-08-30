import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "postgresql",
  schema: "./db/schema.ts",
  out: "./drizzle",
  dbCredentials: {
    // Only needed for migrate/push/studio; `generate` works without a database.
    url: process.env.DATABASE_URL ?? "",
  },
});
