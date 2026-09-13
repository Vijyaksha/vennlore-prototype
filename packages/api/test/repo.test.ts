import { describe, expect, test } from "vitest";

import { memoryRepo, type RecRow, type TalkRow } from "../src/repo";

const talk = (o: Partial<TalkRow> & { id: number }): TalkRow => ({
  externalId: null, title: `Talk ${o.id}`, abstract: "", units: [], topics: [], type: null,
  isInvited: false, isWithdrawn: false, start: null, end: null, sortOrder: null,
  presentationLocation: null, authorIds: [], presenterIds: [], publicationReference: null,
  fundingAcknowledgement: null, teamAcknowledgement: null, sessionId: null, sessionTitle: null,
  sessionCode: null, sessionType: null, sessionTopics: [], building: null, room: null, ...o,
});
const rec = (forTalkId: number, candidateId: number, o: Partial<RecRow> = {}): RecRow => ({
  engineId: "graph_v1", forTalkId, candidateId, score: 0.5, rank: 1, match: true,
  crossDomain: false, why: "", strongestParallel: "", sharedMethods: [], evidence: {},
  runId: "r", contractVersion: 1, ...o,
});

const talks = [
  talk({ id: 0 }),
  talk({ id: 10, presenterIds: [7], authorIds: [7, 8] }),
  talk({ id: 11, presenterIds: [7], authorIds: [7] }),
  talk({ id: 12, presenterIds: [9], authorIds: [8, 9] }),
  talk({ id: 13 }),
];
const recs = [
  rec(10, 13, { rank: 1, score: 0.9 }), rec(10, 12, { rank: 2, score: 0.6 }),
  rec(11, 13, { rank: 1 }), rec(10, 13, { engineId: "other", rank: 1 }),
  rec(0, 13, { match: false }),
];
const repo = memoryRepo(talks, recs);

describe("memoryRepo", () => {
  test("getTalk / getTalks", async () => {
    expect((await repo.getTalk(10))?.id).toBe(10);
    expect(await repo.getTalk(999)).toBeNull();
    expect((await repo.getTalks([13, 10])).map((t) => t.id)).toEqual([10, 13]);
  });
  test("anchorsFor returns the presenter's talks in id order", async () => {
    expect((await repo.anchorsFor(7)).map((t) => t.id)).toEqual([10, 11]);
    expect(await repo.anchorsFor(404)).toEqual([]);
  });
  test("authoredBy returns every talk the person authored", async () => {
    expect(await repo.authoredBy(8)).toEqual(new Set([10, 12]));
  });
  test("getMatches filters by engine and match, orders by anchor then rank, joins the candidate", async () => {
    const rows = await repo.getMatches([10, 11], "graph_v1");
    expect(rows.map((r) => [r.forTalkId, r.candidateId, r.rank])).toEqual([[10, 13, 1], [10, 12, 2], [11, 13, 1]]);
    expect(rows[0]?.candidate.id).toBe(13);
  });
  test("getMatches for another engine sees only its rows", async () => {
    expect((await repo.getMatches([10], "other")).map((r) => r.candidateId)).toEqual([13]);
  });
});
