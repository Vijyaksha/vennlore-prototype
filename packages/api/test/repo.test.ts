import { describe, expect, test } from "vitest";

import { memoryRepo, type RecRow, type TalkRow } from "../src/repo";

const talk = (o: Partial<TalkRow> & { id: number }): TalkRow => ({
  external_id: null, title: `Talk ${o.id}`, abstract: "", units: [], topics: [], type: null,
  is_invited: false, is_withdrawn: false, start: null, end: null, sort_order: null,
  presentation_location: null, author_ids: [], presenter_ids: [], publication_reference: null,
  funding_acknowledgement: null, team_acknowledgement: null, session_id: null, session_title: null,
  session_code: null, session_type: null, session_topics: [], building: null, room: null, ...o,
});
const rec = (for_talk_id: number, candidate_id: number, o: Partial<RecRow> = {}): RecRow => ({
  engine_id: "graph_v1", for_talk_id, candidate_id, score: 0.5, rank: 1, match: true,
  cross_domain: false, why: "", strongest_parallel: "", shared_methods: [], evidence: {},
  run_id: "r", contract_version: 1, ...o,
});

const talks = [
  talk({ id: 13 }),
  talk({ id: 0 }),
  talk({ id: 11, presenter_ids: [7], author_ids: [7] }),
  talk({ id: 10, presenter_ids: [7], author_ids: [7, 8] }),
  talk({ id: 12, presenter_ids: [9], author_ids: [8, 9] }),
];
const recs = [
  rec(11, 13, { rank: 1 }), rec(10, 12, { rank: 2, score: 0.6 }), rec(10, 13, { rank: 1, score: 0.9 }),
  rec(10, 11, { rank: 3, match: false }),
  rec(10, 999, { rank: 4 }),
  rec(10, 13, { engine_id: "other", rank: 1 }),
  rec(10, 11, { rank: 9, contract_version: 2 }),
];
const repo = memoryRepo(talks, recs);

describe("memoryRepo", () => {
  test("getTalk", async () => {
    expect((await repo.getTalk(10))?.id).toBe(10);
    expect(await repo.getTalk(999)).toBeNull();
  });
  test("anchorsFor returns the presenter's talks in id order", async () => {
    expect((await repo.anchorsFor(7)).map((t) => t.id)).toEqual([10, 11]);
    expect(await repo.anchorsFor(404)).toEqual([]);
  });
  test("getMatches filters by engine and match, orders by anchor then rank, joins the candidate", async () => {
    const rows = await repo.getMatches([10, 11], "graph_v1");
    expect(rows.map((r) => [r.for_talk_id, r.candidate_id, r.rank])).toEqual([[10, 13, 1], [10, 12, 2], [11, 13, 1]]);
    expect(rows[0]?.candidate.id).toBe(13);
    expect(await repo.getMatches([], "graph_v1")).toEqual([]);
  });
  test("getMatches for another engine sees only its rows", async () => {
    expect((await repo.getMatches([10], "other")).map((r) => r.candidate_id)).toEqual([13]);
  });
  test("getMatches ignores rows written under another contract version", async () => {
    expect((await repo.getMatches([10], "graph_v1")).map((r) => r.candidate_id)).not.toContain(11);
  });
  test("getMatches breaks rank ties by candidate_id", async () => {
    const tied = memoryRepo(talks, [rec(10, 13, { rank: 1 }), rec(10, 12, { rank: 1 })]);
    expect((await tied.getMatches([10], "graph_v1")).map((r) => r.candidate_id)).toEqual([12, 13]);
  });
});
