// Reports which implementation of each swappable part is equipped: matching
// engine, UI, data layer. Run by the SessionStart hook (.claude/settings.json)
// and by `npm run status`. Reads config; never connects to anything.
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_ENGINE = "graph_v1"; // mirrors createContext in packages/api/src/trpc.ts

/** Engine ids registered in the Python registry, in file order. */
function registeredEngines(root) {
  const src = readFileSync(join(root, "pipeline/src/gps_core/registry.py"), "utf8");
  const block = src.slice(src.indexOf("ENGINES"), src.indexOf("}", src.indexOf("ENGINES")));
  return [...block.matchAll(/"([a-z0-9_]+)"\s*:/g)].map((m) => m[1]);
}

/** ENGINE_ID from the environment, else from packages/api/.env, else the server default. */
function activeEngine(root, env) {
  if (env.ENGINE_ID?.trim()) return { active: env.ENGINE_ID.trim(), source: "ENGINE_ID env" };
  const envFile = join(root, "packages/api/.env");
  if (existsSync(envFile)) {
    const m = readFileSync(envFile, "utf8").match(/^ENGINE_ID=(.+)$/m);
    if (m) return { active: m[1].trim(), source: "packages/api/.env" };
  }
  return { active: DEFAULT_ENGINE, source: "default" };
}

/** Apps under apps/; the one depending on @repo/api is the UI that mounts the API. */
function uis(root) {
  const apps = readdirSync(join(root, "apps")).filter((d) => existsSync(join(root, "apps", d, "package.json"))).sort();
  const mounts = apps.filter((d) => {
    const pkg = JSON.parse(readFileSync(join(root, "apps", d, "package.json"), "utf8"));
    return "@repo/api" in (pkg.dependencies ?? {});
  });
  return { registered: apps, active: mounts[0] ?? null };
}

export function loadedParts(root, env = process.env) {
  const registered = registeredEngines(root);
  return {
    engines: { registered, ...activeEngine(root, env) },
    uis: uis(root),
    dataLayer: { active: "@repo/api", registered: ["@repo/api"] },
  };
}

const only = (list) => (list.length === 1 ? " (only one registered)" : "");

export function render(p) {
  return [
    "Loaded parts (contract at packages/contracts):",
    `  engine: ${p.engines.active} (${p.engines.source}); registered: ${p.engines.registered.join(", ")}${only(p.engines.registered)}; switch with ENGINE_ID (serve) / ENGINE (run)`,
    `  ui: ${p.uis.active ?? "none"} (mounts @repo/api); apps: ${p.uis.registered.join(", ")}`,
    `  data layer: ${p.dataLayer.active} (single implementation)`,
  ].join("\n");
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const root = join(dirname(fileURLToPath(import.meta.url)), "..");
  console.log(render(loadedParts(root)));
}
