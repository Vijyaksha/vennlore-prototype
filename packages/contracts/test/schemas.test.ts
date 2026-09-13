import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";

import {
  AgendaResponseSchema,
  PicksResponseSchema,
  RecommendationSchema,
  SCHEMAS,
  SubjectSchema,
  TalkSchema,
  emitAll,
} from "../src/index";

const ROOT = join(import.meta.dirname, "..");
const read = (p: string) => JSON.parse(readFileSync(join(ROOT, p), "utf8"));

describe("valid fixtures parse", () => {
  for (const kind of Object.keys(SCHEMAS) as (keyof typeof SCHEMAS)[]) {
    test(kind, () => {
      const row = read(`fixtures/valid/${kind}.json`);
      expect(SCHEMAS[kind].safeParse(row).success).toBe(true);
    });
  }
});

const EXPECTED_PATH: Record<string, string> = {
  "recommendation-score-out-of-range.json": "score",
  "recommendation-unknown-key.json": "same_method",
  "talk-missing-title.json": "title",
};

describe("invalid fixtures are rejected", () => {
  for (const file of readdirSync(join(ROOT, "fixtures/invalid"))) {
    test(file, () => {
      const kind = file.split("-")[0] as keyof typeof SCHEMAS;
      const row = read(`fixtures/invalid/${file}`);
      const result = SCHEMAS[kind].safeParse(row);
      expect(result.success).toBe(false);
      const issues = result.error!.issues;
      const paths = issues.map((i) => i.path.join("."));
      const keys = issues.flatMap((i) => ("keys" in i ? i.keys : []));
      expect([...paths, ...keys]).toContain(EXPECTED_PATH[file]);
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

test("every committed schema file has an emitter entry and vice versa", () => {
  expect(readdirSync(join(ROOT, "schema")).sort()).toEqual(
    Object.keys(emitAll())
      .map((k) => `${k}.schema.json`)
      .sort(),
  );
});

test("talk has exactly 25 fields", () => {
  expect(Object.keys(TalkSchema.shape)).toHaveLength(25);
});

test("recommendation has exactly 13 fields", () => {
  expect(Object.keys(RecommendationSchema.shape)).toHaveLength(13);
});

describe("api schemas", () => {
  test("subject accepts exactly one of presenter_id or talk_id", () => {
    expect(SubjectSchema.safeParse({ presenter_id: 7 }).success).toBe(true);
    expect(SubjectSchema.safeParse({ talk_id: 0 }).success).toBe(true);
    expect(SubjectSchema.safeParse({ talk_id: 0, engine_id: "other" }).success).toBe(true);
    expect(SubjectSchema.safeParse({ presenter_id: 7, talk_id: 0 }).success).toBe(false);
    expect(SubjectSchema.safeParse({ presenter_id: 0 }).success).toBe(false);
    expect(SubjectSchema.safeParse({ talk_id: 0, engine_id: "DROP TABLE" }).success).toBe(false);
    expect(SubjectSchema.safeParse({ talk_id: 0, engine_id: "a".repeat(65) }).success).toBe(false);
  });
  test("picks response embeds contract rows and a candidate per recommendation", () => {
    const row = read("fixtures/valid/picks_response.json");
    expect(PicksResponseSchema.safeParse(row).success).toBe(true);
    const bad = { ...row, recommendations: [{ ...row.recommendations[0], candidate: undefined }] };
    expect(PicksResponseSchema.safeParse(bad).success).toBe(false);
  });
  test("agenda response items carry kind, units and transit", () => {
    const row = read("fixtures/valid/agenda_response.json");
    expect(AgendaResponseSchema.safeParse(row).success).toBe(true);
    const bad = structuredClone(row);
    bad.days[0].items[0].kind = "later";
    expect(AgendaResponseSchema.safeParse(bad).success).toBe(false);
  });
});
