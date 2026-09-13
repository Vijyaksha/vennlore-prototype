import { describe, expect, test } from "vitest";

import { appRouter } from "../src/router";
import { createCallerFactory } from "../src/trpc";
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

const anchor = talk({ id: 0, title: "Porphyrin nanorods" });
const mine1 = talk({ id: 10, title: "My first talk", presenterIds: [7], authorIds: [7], start: new Date("2026-03-19T14:00:00Z"), end: new Date("2026-03-19T14:12:00Z"), building: "Convention Center", room: "Bluebird 2A" });
const mine2 = talk({ id: 11, title: "My second talk", presenterIds: [7], authorIds: [7] });
const bluebird = talk({ id: 2802, title: "Bluebird talk", units: ["DPOLY"], start: new Date("2026-03-19T15:12:00Z"), end: new Date("2026-03-19T15:24:00Z"), building: "Convention Center", room: "Bluebird 3C" });
const hall = talk({ id: 12342, title: "Hall talk", units: ["FIAP"], start: new Date("2026-03-19T16:00:00Z"), end: new Date("2026-03-19T16:12:00Z"), building: "Convention Center", room: "Exhibit Hall D, E & F, Level 2" });
const repo = memoryRepo([anchor, mine1, mine2, bluebird, hall], [
  rec(0, 2802, { rank: 1, score: 0.8 }), rec(0, 12342, { rank: 2, score: 0.4, crossDomain: true }),
  rec(10, 2802, { rank: 1, score: 0.9 }), rec(11, 12342, { rank: 1, score: 0.7, crossDomain: true }),
  rec(10, 12342, { rank: 2, score: 0.3, match: false }),
  rec(0, 2802, { engineId: "other", rank: 1, score: 0.1 }),
]);
const call = (engineId = "graph_v1") => createCallerFactory(appRouter)({ repo, engineId });

describe("talk.get", () => {
  test("returns the talk or NOT_FOUND", async () => {
    expect((await call().talk.get({ id: 2802 })).title).toBe("Bluebird talk");
    await expect(call().talk.get({ id: 1 })).rejects.toThrow(/not found/i);
  });
});

describe("presenter.picks", () => {
  test("by talkId (single-tenant anchor): anchors = [talk], matched rows of the configured engine only", async () => {
    const r = await call().presenter.picks({ talkId: 0 });
    expect(r.anchors.map((t) => t.id)).toEqual([0]);
    expect(r.recommendations.map((x) => [x.candidateId, x.rank, x.score])).toEqual([[2802, 1, 0.8], [12342, 2, 0.4]]);
    expect(r.recommendations[0]?.candidate.title).toBe("Bluebird talk");
  });
  test("by presenterId: union across the presenter's anchors, per anchor order", async () => {
    const r = await call().presenter.picks({ presenterId: 7 });
    expect(r.presenterId).toBe(7);
    expect(r.anchors.map((t) => t.id)).toEqual([10, 11]);
    expect(r.recommendations.map((x) => [x.forTalkId, x.candidateId])).toEqual([[10, 2802], [11, 12342]]);
  });
  test("engineId override selects another engine's rows", async () => {
    const r = await call().presenter.picks({ talkId: 0, engineId: "other" });
    expect(r.recommendations.map((x) => x.score)).toEqual([0.1]);
  });
  test("unknown presenter → NOT_FOUND", async () => {
    await expect(call().presenter.picks({ presenterId: 404 })).rejects.toThrow(/not found/i);
  });
});

describe("presenter.agenda", () => {
  test("own timed talks plus matched candidates, grouped by Denver day with transit", async () => {
    const r = await call().presenter.agenda({ presenterId: 7 });
    expect(r.days.map((d) => d.date)).toEqual(["2026-03-19"]);
    expect(r.days[0]?.items.map((i) => [i.id, i.kind])).toEqual([[10, "mine"], [2802, "core"], [12342, "surprise"]]);
    expect(r.days[0]?.items[1]?.transit).toEqual({ walk: 15, slack: 45, tight: false });
  });
  test("by talkId works for the untimed anchor: only candidates appear", async () => {
    const r = await call().presenter.agenda({ talkId: 0 });
    expect(r.days.flatMap((d) => d.items.map((i) => i.id))).toEqual([2802, 12342]);
  });
});
