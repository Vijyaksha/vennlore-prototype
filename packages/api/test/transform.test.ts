import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { describe, expect, test } from "vitest";

import { toRecommendationInsert, toRunInsert, toSeedFile, toTalkInsert } from "../src/db/transform";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"));

describe("toSeedFile", () => {
  test("accepts a contract-shaped seed and validates every row", () => {
    const seed = toSeedFile({
      contract_version: 1, talks: [fixture("talk")], locations: [],
      recommendations: [fixture("recommendation")], runs: [fixture("run")],
    });
    expect(seed.talks).toHaveLength(1);
  });
  test("rejects a row that breaks the contract, naming the row", () => {
    expect(() => toSeedFile({
      contract_version: 1, talks: [{ ...fixture("talk"), title: "" }], locations: [], recommendations: [], runs: [],
    })).toThrow(/talks\[0\]/);
  });
  test("rejects an unknown contract version", () => {
    expect(() => toSeedFile({ contract_version: 2, talks: [], locations: [], recommendations: [], runs: [] }))
      .toThrow(/contract_version/);
  });
});

describe("row transforms", () => {
  test("talk: snake_case → camelCase, ISO strings → Date, lists kept", () => {
    const row = toTalkInsert(fixture("talk"));
    expect(row.id).toBe(2802);
    expect(row.externalId).toBe("SMT26-3750532");
    expect(row.start).toEqual(new Date("2026-03-19T15:12:00.000Z"));
    expect(row.authorIds).toEqual([101, 102]);
    expect(row.sessionCode).toBe("MAR-B31");
    expect(Object.keys(row)).toHaveLength(25);
  });
  test("recommendation keeps evidence as-is and shared_methods as an array", () => {
    const row = toRecommendationInsert(fixture("recommendation"));
    expect(row.engineId).toBe("graph_v1");
    expect(row.score).toBe(0.8);
    expect(row.evidence).toEqual({ same_method: 4, specificity: 3, usage_parallel: 5, rubric_sum: 12 });
    expect(row.sharedMethods).toEqual(["transient photocurrent measurement"]);
    expect(row.contractVersion).toBe(1);
  });
  test("run converts timestamps", () => {
    const row = toRunInsert(fixture("run"));
    expect(row.startedAt).toEqual(new Date("2026-09-12T12:00:00Z"));
    expect(row.anchorIds).toEqual([0]);
  });
});
