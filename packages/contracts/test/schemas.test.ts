import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";

import { RecommendationSchema, RunSchema, TalkSchema } from "../src/index.js";
import { emitAll } from "../scripts/emit.js";

const ROOT = join(import.meta.dirname, "..");
const read = (p: string) => JSON.parse(readFileSync(join(ROOT, p), "utf8"));

const BY_KIND = {
  talk: TalkSchema,
  recommendation: RecommendationSchema,
  run: RunSchema,
} as const;

describe("valid fixtures parse", () => {
  for (const kind of Object.keys(BY_KIND) as (keyof typeof BY_KIND)[]) {
    test(kind, () => {
      const row = read(`fixtures/valid/${kind}.json`);
      expect(BY_KIND[kind].safeParse(row).success).toBe(true);
    });
  }
});

describe("invalid fixtures are rejected", () => {
  for (const file of readdirSync(join(ROOT, "fixtures/invalid"))) {
    test(file, () => {
      const kind = file.split("-")[0] as keyof typeof BY_KIND;
      const row = read(`fixtures/invalid/${file}`);
      expect(BY_KIND[kind].safeParse(row).success).toBe(false);
    });
  }
});

describe("committed JSON Schema matches the zod source", () => {
  for (const [kind, schema] of Object.entries(emitAll())) {
    test(kind, () => {
      expect(read(`schema/${kind}.schema.json`)).toEqual(schema);
    });
  }
});

test("talk has exactly 25 fields", () => {
  expect(Object.keys(TalkSchema.shape)).toHaveLength(25);
});

test("recommendation has exactly 13 fields", () => {
  expect(Object.keys(RecommendationSchema.shape)).toHaveLength(13);
});
