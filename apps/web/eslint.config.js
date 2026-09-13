import { nextJsConfig } from "@repo/eslint-config/next-js";

/** @type {import("eslint").Linter.Config[]} */
export default [
  ...nextJsConfig,
  {
    rules: {
      // The app meets the data layer only through @repo/api's public surface.
      "no-restricted-imports": [
        "error",
        {
          paths: [
            { name: "drizzle-orm", message: "Database access lives in @repo/api." },
            { name: "postgres", message: "Database access lives in @repo/api." },
          ],
          patterns: [
            { group: ["drizzle-orm/*"], message: "Database access lives in @repo/api." },
            { group: ["@repo/api/*"], message: "Import from the @repo/api barrel only." },
          ],
        },
      ],
    },
  },
];
