import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { RecommendationSchema, RunSchema, TalkSchema } from "@repo/contracts";
import { describe, expect, test } from "vitest";

import {
  toLocationInsert, toRecommendationInsert, toRunInsert, toSeedFile, toTalkInsert,
} from "../src/db/transform";

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

const camel = (k: string) => k.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());
const DATE_KEYS = new Set(["start", "end", "started_at", "finished_at"]);
function expectRoundTrip(input: Record<string, unknown>, row: Record<string, unknown>) {
  expect(Object.keys(row).sort()).toEqual(Object.keys(input).map(camel).sort());
  for (const [k, v] of Object.entries(input))
    expect(row[camel(k)], k).toEqual(DATE_KEYS.has(k) && v !== null ? new Date(v as string) : v);
}

describe("round trip: every contract field lands on its own column", () => {
  test("talk", () => {
    const talk = TalkSchema.parse({
      ...fixture("talk"),
      is_invited: true, is_withdrawn: false,
      presentation_location: "Poster board 12",
      publication_reference: "Phys. Rev. B 110, 045101",
      funding_acknowledgement: "NSF DMR-2401234",
      team_acknowledgement: "Thanks to the cleanroom staff",
      session_title: "Organic Electronics & Photonics", session_code: "MAR-B31", session_type: "ORAL",
      start: "2026-03-19T15:12:00.000Z", end: "2026-03-19T15:24:00.000Z",
    });
    expectRoundTrip(talk, toTalkInsert(talk));
  });
  test("recommendation", () => {
    const rec = RecommendationSchema.parse({
      ...fixture("recommendation"), match: true, cross_domain: false,
      why: "Both read carrier dynamics.", strongest_parallel: "Time-resolved photocurrent.",
    });
    expectRoundTrip(rec, toRecommendationInsert(rec));
  });
  test("run", () => {
    const run = RunSchema.parse({
      ...fixture("run"), started_at: "2026-09-12T12:00:00Z", finished_at: "2026-09-12T12:00:34Z",
    });
    expectRoundTrip(run, toRunInsert(run));
  });
});

describe("locations", () => {
  test("accepts an id above int32 and maps it unchanged", () => {
    const location = { id: 4109684556, building: "Convention Center", room: "Bluebird 3C" };
    const seed = toSeedFile({ contract_version: 1, talks: [], locations: [location], recommendations: [], runs: [] });
    expect(toLocationInsert(seed.locations[0]!)).toEqual(location);
  });
  test("rejects an empty room, naming the row", () => {
    expect(() => toSeedFile({
      contract_version: 1, talks: [], recommendations: [], runs: [],
      locations: [{ id: 1, building: "Convention Center", room: "" }],
    })).toThrow(/locations\[0\]/);
  });
});
