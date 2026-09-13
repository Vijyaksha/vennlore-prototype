import { readFileSync } from "node:fs";

import { describe, expect, test } from "vitest";

import { resolveSeedPath } from "../src/db/seed-path";
import { toSeedFile, toTalkInsert, type SeedFile } from "../src/db/transform";
import { memoryRepo, type RecRow, type TalkRow } from "../src/repo";
import { dbRepo } from "../src/repo.db";

// Runs only where a seeded Postgres exists (the e2e CI job). Read-only.
const url = process.env.DATABASE_URL;
const seedPath = resolveSeedPath(process.env, "");
// vitest still collects a skipped describe body, so the seed is only read when it will be used.
const enabled = Boolean(url) && seedPath !== "";
const EMPTY = { contract_version: 1, talks: [], locations: [], recommendations: [], runs: [] } as SeedFile;
describe.skipIf(!enabled)("memoryRepo and dbRepo agree on the seeded store", () => {
  const seed = enabled ? toSeedFile(JSON.parse(readFileSync(seedPath, "utf8"))) : EMPTY;
  const fake = memoryRepo(seed.talks.map(toTalkInsert) as TalkRow[], seed.recommendations as RecRow[]);
  const talkIds = seed.talks.map((t) => t.id);
  const presenterIds = [...new Set(seed.talks.flatMap((t) => t.presenter_ids))];
  const anchors = [...new Set(seed.recommendations.map((r) => r.for_talk_id))];
  const engines = [...new Set(seed.recommendations.map((r) => r.engine_id))];

  test("getTalk", async () => {
    for (const id of [...talkIds, 999_999]) expect(await dbRepo.getTalk(id)).toEqual(await fake.getTalk(id));
  });
  test("anchorsFor", async () => {
    for (const p of [...presenterIds, 404]) expect(await dbRepo.anchorsFor(p)).toEqual(await fake.anchorsFor(p));
  });
  test("getMatches: same rows, same order, same candidates", async () => {
    for (const e of [...engines, "other"]) expect(await dbRepo.getMatches(anchors, e)).toEqual(await fake.getMatches(anchors, e));
    expect(await dbRepo.getMatches([], engines[0]!)).toEqual([]);
  });
});
