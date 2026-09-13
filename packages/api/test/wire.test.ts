import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { describe, expect, test } from "vitest";

import { PickSchema, RecommendationSchema, TalkSchema } from "@repo/contracts";

import { toRecommendationInsert, toTalkInsert } from "../src/db/transform";
import type { RecRow, TalkRow } from "../src/repo";
import { toPick, toRecommendation, toTalk } from "../src/wire";

const req = createRequire(import.meta.url);
const fixture = (kind: string) =>
  JSON.parse(readFileSync(req.resolve(`@repo/contracts/fixtures/valid/${kind}.json`), "utf8"));

// toTalkInsert / toRecommendationInsert set every column, so the insert shape is a full row.
const talkRow = () => toTalkInsert(TalkSchema.parse(fixture("talk"))) as TalkRow;
const recRow = () => toRecommendationInsert(RecommendationSchema.parse(fixture("recommendation"))) as RecRow;

describe("wire: Drizzle row -> contract row", () => {
  test("toTalk round-trips the talk fixture exactly", () => {
    expect(toTalk(talkRow())).toEqual(fixture("talk"));
  });
  test("toTalk emits ISO timestamps and nulls, and validates", () => {
    const t = toTalk({ ...talkRow(), start: null, end: new Date("2026-03-19T15:24:00Z") });
    expect(t.start).toBeNull();
    expect(t.end).toBe("2026-03-19T15:24:00.000Z");
    expect(TalkSchema.safeParse(t).success).toBe(true);
  });
  test("toRecommendation round-trips the recommendation fixture exactly", () => {
    expect(toRecommendation(recRow())).toEqual(fixture("recommendation"));
  });
  test("a row whose contract_version is not 1 fails the contract", () => {
    const r = toRecommendation({ ...recRow(), contractVersion: 2 });
    expect(r.contract_version).toBe(2);
    expect(RecommendationSchema.safeParse(r).success).toBe(false);
  });
  test("toPick joins the candidate and validates against PickSchema", () => {
    const pick = toPick({ ...recRow(), candidate: talkRow() });
    expect(pick.candidate.id).toBe(2802);
    expect(PickSchema.safeParse(pick).success).toBe(true);
    expect(Object.keys(pick)).toHaveLength(14);
  });
});
