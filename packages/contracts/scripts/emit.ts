import { mkdirSync, realpathSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { emitAll } from "../src/schemas.js";

const isMain =
  process.argv[1] !== undefined && realpathSync(process.argv[1]) === realpathSync(import.meta.filename);

if (isMain) {
  const dir = join(import.meta.dirname, "..", "schema");
  mkdirSync(dir, { recursive: true });
  for (const [kind, schema] of Object.entries(emitAll())) {
    writeFileSync(join(dir, `${kind}.schema.json`), JSON.stringify(schema, null, 2) + "\n");
  }
  console.log("emitted talk, recommendation, run");
}
