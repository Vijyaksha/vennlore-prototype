import { nextJsConfig } from "@repo/eslint-config/next-js";

// The database-driver guards live in the shared config so every Next app gets
// them; only-warn means this package's --max-warnings 0 is what enforces them.
/** @type {import("eslint").Linter.Config[]} */
export default nextJsConfig;
