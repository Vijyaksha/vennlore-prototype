import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "postgresql",
  schema: "./db/schema.ts",
  out: "./drizzle",
  dbCredentials: {
    // Only migrate/push/studio read this; `generate` works without a database.
    get url(): string {
      const url = process.env.DATABASE_URL;
      if (!url) {
        throw new Error("DATABASE_URL is not set — connect Supabase first");
      }
      return url;
    },
  },
});
