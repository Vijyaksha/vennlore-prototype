import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { loadedParts, render } from "./loaded-parts.mjs";

/** A minimal repo: two engines registered, two apps, only one mounting @repo/api. */
function fakeRepo({ engineId } = {}) {
  const root = mkdtempSync(join(tmpdir(), "loaded-parts-"));
  mkdirSync(join(root, "pipeline/src/gps_core"), { recursive: true });
  writeFileSync(
    join(root, "pipeline/src/gps_core/registry.py"),
    'ENGINES: dict[str, str] = {\n    "graph_v1": "gps_engines.graph_v1.engine:build",\n    "embed_v1": "gps_engines.embed_v1.engine:build",\n}\n',
  );
  for (const [app, deps] of [["web", { "@repo/api": "*" }], ["docs", {}]]) {
    mkdirSync(join(root, "apps", app), { recursive: true });
    writeFileSync(join(root, "apps", app, "package.json"), JSON.stringify({ name: app, dependencies: deps }));
  }
  mkdirSync(join(root, "packages/api"), { recursive: true });
  writeFileSync(join(root, "packages/api/package.json"), JSON.stringify({ name: "@repo/api" }));
  if (engineId !== undefined) writeFileSync(join(root, "packages/api/.env"), `DATABASE_URL=postgres://x\nENGINE_ID=${engineId}\n`);
  return root;
}

test("reports the registered engines and the default active one", () => {
  const parts = loadedParts(fakeRepo(), {});
  assert.deepEqual(parts.engines.registered, ["graph_v1", "embed_v1"]);
  assert.equal(parts.engines.active, "graph_v1");
  assert.equal(parts.engines.source, "default");
});

test("ENGINE_ID in the environment wins over the api .env file", () => {
  assert.equal(loadedParts(fakeRepo({ engineId: "embed_v1" }), {}).engines.active, "embed_v1");
  assert.equal(loadedParts(fakeRepo({ engineId: "embed_v1" }), { ENGINE_ID: "graph_v1" }).engines.active, "graph_v1");
});

test("lists the UIs and marks the one that mounts the API as active", () => {
  const parts = loadedParts(fakeRepo(), {});
  assert.deepEqual(parts.uis.registered, ["docs", "web"]);
  assert.equal(parts.uis.active, "web");
  assert.equal(parts.dataLayer.active, "@repo/api");
});

test("render says when only one option exists and names the switch", () => {
  const text = render(loadedParts(fakeRepo(), {}));
  assert.match(text, /engine: graph_v1 \(default\); registered: graph_v1, embed_v1; switch with ENGINE_ID/);
  assert.match(text, /ui: web \(mounts @repo\/api\); apps: docs, web/);
  assert.match(text, /data layer: @repo\/api \(single implementation\)/);
});
