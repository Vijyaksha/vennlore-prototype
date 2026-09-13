import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { z } from "zod";

import { RecommendationSchema, RunSchema, TalkSchema } from "../src/index.js";

export function emitAll(): Record<string, Record<string, unknown>> {
  const opts = { target: "draft-2020-12" as const };
  return {
    talk: z.toJSONSchema(TalkSchema, opts),
    recommendation: z.toJSONSchema(RecommendationSchema, opts),
    run: z.toJSONSchema(RunSchema, opts),
  };
}

if (process.argv[1]?.endsWith("emit.ts")) {
  const dir = join(import.meta.dirname, "..", "schema");
  mkdirSync(dir, { recursive: true });
  for (const [kind, schema] of Object.entries(emitAll())) {
    writeFileSync(join(dir, `${kind}.schema.json`), JSON.stringify(schema, null, 2) + "\n");
  }
  console.log("emitted talk, recommendation, run");
}
