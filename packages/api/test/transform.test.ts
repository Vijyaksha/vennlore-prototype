import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { RunSchema, TalkSchema } from "@repo/contracts";
import { describe, expect, test } from "vitest";

import { toRunInsert, toSeedFile, toTalkInsert } from "../src/db/transform";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"));


const base = () => ({
  contract_version: 1, talks: [fixture("talk")], locations: [],
  recommendations: [fixture("recommendation")], runs: [fixture("run")],
});
// fixture recommendation: for_talk_id 0, candidate_id 12772, run_id "graph_v1-20260912T120000Z-a1b2c3"; fixture talk id 2802.
const withTalks = (ids: number[]) => ({ ...base(), talks: ids.map((id) => ({ ...fixture("talk"), id })) });

describe("toSeedFile", () => {
  test("accepts a contract-shaped seed and validates every row", () => {
    const seed = toSeedFile(withTalks([0, 12772]));
    expect(seed.talks).toHaveLength(2);
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
    expect(row.external_id).toBe("SMT26-3750532");
    expect(row.start).toEqual(new Date("2026-03-19T15:12:00.000Z"));
    expect(row.author_ids).toEqual([101, 102]);
    expect(row.session_code).toBe("MAR-B31");
    expect(Object.keys(row)).toHaveLength(25);
  });
  test("run converts timestamps", () => {
    const row = toRunInsert(fixture("run"));
    expect(row.started_at).toEqual(new Date("2026-09-12T12:00:00Z"));
    expect(row.anchor_ids).toEqual([0]);
  });
});

const DATE_KEYS = new Set(["start", "end", "started_at", "finished_at"]);
// Since the rename a column's property name is its contract field name, so the keys must match exactly.
function expectRoundTrip(input: Record<string, unknown>, row: Record<string, unknown>) {
  expect(Object.keys(row).sort()).toEqual(Object.keys(input).sort());
  for (const [k, v] of Object.entries(input))
    expect(row[k], k).toEqual(DATE_KEYS.has(k) && v !== null ? new Date(v as string) : v);
}

describe("round trip: every contract field lands on its own column", () => {
  test("talk", () => {
    const talk = TalkSchema.parse({
      ...fixture("talk"),
      is_invited: true,
      presentation_location: "Poster board 12",
      publication_reference: "Phys. Rev. B 110, 045101",
      funding_acknowledgement: "NSF DMR-2401234",
      team_acknowledgement: "Thanks to the cleanroom staff",
      session_topics: ["Photonics"],
    });
    expectRoundTrip(talk, toTalkInsert(talk));
  });
  test("run", () => {
    const run = RunSchema.parse({
      ...fixture("run"), started_at: "2026-09-12T12:00:00Z", finished_at: "2026-09-12T12:00:34Z",
    });
    expectRoundTrip(run, toRunInsert(run));
  });
});

describe("locations", () => {
  test("accepts an id above int32 and carries it unchanged", () => {
    const location = { id: 4109684556, building: "Convention Center", room: "Bluebird 3C" };
    const seed = toSeedFile({ contract_version: 1, talks: [], locations: [location], recommendations: [], runs: [] });
    expect(seed.locations[0]).toEqual(location);
  });
  test("rejects an empty room, naming the row", () => {
    expect(() => toSeedFile({
      contract_version: 1, talks: [], recommendations: [], runs: [],
      locations: [{ id: 1, building: "Convention Center", room: "" }],
    })).toThrow(/locations\[0\]/);
  });
});

describe("toSeedFile referential checks", () => {
  test("rejects a recommendation whose candidate_id has no talk", () => {
    const seed = withTalks([0]); // candidate 12772 missing
    expect(() => toSeedFile(seed)).toThrow(/recommendations\[0\]\.candidate_id.*no talk 12772/);
  });
  test("rejects a recommendation whose for_talk_id has no talk", () => {
    const seed = withTalks([12772]); // anchor 0 missing
    expect(() => toSeedFile(seed)).toThrow(/recommendations\[0\]\.for_talk_id.*no talk 0/);
  });
  test("rejects a recommendation whose run_id has no run", () => {
    const seed = { ...withTalks([0, 12772]), runs: [{ ...fixture("run"), run_id: "other-run" }] };
    expect(() => toSeedFile(seed)).toThrow(/recommendations\[0\]\.run_id.*no run/);
  });
  test("rejects duplicate talk ids, run ids, location ids and recommendation keys", () => {
    const ok = withTalks([0, 12772]);
    expect(() => toSeedFile({ ...ok, talks: [...ok.talks, ok.talks[0]] })).toThrow(/talks\[2\]\.id.*duplicate/);
    expect(() => toSeedFile({ ...ok, runs: [ok.runs[0], ok.runs[0]] })).toThrow(/runs\[1\]\.run_id.*duplicate/);
    expect(() => toSeedFile({ ...ok, locations: [{ id: 1, building: "A", room: "1" }, { id: 1, building: "A", room: "2" }] })).toThrow(/locations\[1\]\.id.*duplicate/);
    expect(() => toSeedFile({ ...ok, recommendations: [ok.recommendations[0], ok.recommendations[0]] })).toThrow(/recommendations\[1\].*duplicate/);
  });
  test("accepts a seed whose references all resolve", () => {
    expect(toSeedFile(withTalks([0, 12772])).recommendations).toHaveLength(1);
  });
});
