import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { afterEach, describe, expect, test, vi } from "vitest";

import { appRouter } from "../src/router";
import { createCallerFactory, createContext } from "../src/trpc";
import { memoryRepo, type Repo, type RecRow, type TalkRow } from "../src/repo";

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
  rec(11, 10, { rank: 1, score: 0.6 }),
]);
const call = (engineId = "graph_v1", r: Repo = repo) => createCallerFactory(appRouter)({ repo: r, engineId });

afterEach(() => {
  vi.unstubAllEnvs();
});

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
    expect(r.recommendations.map((x) => [x.forTalkId, x.candidateId])).toEqual([[10, 2802], [11, 10], [11, 12342]]);
  });
  test("engineId override selects another engine's rows", async () => {
    const r = await call().presenter.picks({ talkId: 0, engineId: "other" });
    expect(r.recommendations.map((x) => x.score)).toEqual([0.1]);
  });
  test("unknown presenter → NOT_FOUND", async () => {
    await expect(call().presenter.picks({ presenterId: 404 })).rejects.toThrow(/not found/i);
  });
  test("unknown talk → NOT_FOUND", async () => {
    await expect(call().presenter.picks({ talkId: 1 })).rejects.toThrow(/not found/i);
  });
  test("rejects an input naming both presenterId and talkId", async () => {
    await expect(call().presenter.picks({ presenterId: 7, talkId: 0 } as never)).rejects.toThrow();
  });
  test("rejects an engineId outside the contract's engine_id rule", async () => {
    await expect(call().presenter.picks({ talkId: 0, engineId: "DROP TABLE" })).rejects.toThrow();
    await expect(call().presenter.picks({ talkId: 0, engineId: "a".repeat(65) })).rejects.toThrow();
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
  test("a presenter's own talk matched under another of their anchors appears once, as mine", async () => {
    const r = await call().presenter.agenda({ presenterId: 7 });
    const tens = r.days.flatMap((d) => d.items).filter((i) => i.id === 10);
    expect(tens.map((i) => i.kind)).toEqual(["mine"]);
  });
  test("unknown talk → NOT_FOUND", async () => {
    await expect(call().presenter.agenda({ talkId: 1 })).rejects.toThrow(/not found/i);
  });
  test("engineId override selects another engine's rows", async () => {
    const r = await call().presenter.agenda({ talkId: 0, engineId: "other" });
    expect(r.days.flatMap((d) => d.items.map((i) => i.id))).toEqual([2802]);
  });
  test("kind follows the highest-scoring match when a candidate matches under two anchors", async () => {
    const r2 = memoryRepo([mine1, mine2, bluebird], [
      rec(10, 2802, { score: 0.9, crossDomain: true }),
      rec(11, 2802, { score: 0.3, crossDomain: false }),
    ]);
    const r = await call("graph_v1", r2).presenter.agenda({ presenterId: 7 });
    expect(r.days.flatMap((d) => d.items).find((i) => i.id === 2802)?.kind).toBe("surprise");
  });
  test("on equal scores kind follows the first match in getMatches order", async () => {
    const r2 = memoryRepo([mine1, mine2, bluebird], [
      rec(10, 2802, { score: 0.5, crossDomain: false }),
      rec(11, 2802, { score: 0.5, crossDomain: true }),
    ]);
    const r = await call("graph_v1", r2).presenter.agenda({ presenterId: 7 });
    expect(r.days.flatMap((d) => d.items).find((i) => i.id === 2802)?.kind).toBe("core");
  });
  test("on equal start times the presenter's own talk comes first", async () => {
    const early = talk({ id: 5, title: "Same slot", start: mine1.start, end: mine1.end, building: "Convention Center", room: "Bluebird 2B" });
    const r2 = memoryRepo([mine1, early], [rec(10, 5)]);
    const r = await call("graph_v1", r2).presenter.agenda({ presenterId: 7 });
    expect(r.days[0]?.items.map((i) => [i.id, i.kind])).toEqual([[10, "mine"], [5, "core"]]);
  });
});

describe("error masking over HTTP", () => {
  const serve = (r: Repo, path: string, input: unknown) =>
    fetchRequestHandler({
      endpoint: "/api/trpc",
      router: appRouter,
      req: new Request(`http://test/api/trpc/${path}?input=${encodeURIComponent(JSON.stringify(input))}`),
      createContext: () => ({ repo: r, engineId: "graph_v1" }),
    });
  const leaky: Repo = {
    ...repo,
    getTalk: async () => {
      throw new Error("Failed query: select secret");
    },
  };

  test("internal errors reach the client as a generic message without a stack in production", async () => {
    vi.stubEnv("NODE_ENV", "production");
    const res = await serve(leaky, "talk.get", { id: 5 });
    const body = await res.text();
    expect(res.status).toBe(500);
    expect(body).not.toContain("secret");
    expect(body).toContain("Internal server error");
    expect(body).not.toContain("\"stack\"");
  });
  test("NOT_FOUND keeps its message in production", async () => {
    vi.stubEnv("NODE_ENV", "production");
    const res = await serve(repo, "talk.get", { id: 1 });
    expect(res.status).toBe(404);
    expect(await res.text()).toContain("talk 1 not found");
  });
});

describe("createContext", () => {
  test("reads ENGINE_ID, defaulting to graph_v1", () => {
    vi.stubEnv("ENGINE_ID", "x");
    expect(createContext().engineId).toBe("x");
    vi.stubEnv("ENGINE_ID", undefined);
    expect(createContext().engineId).toBe("graph_v1");
  });
  test("does not need DATABASE_URL", () => {
    vi.stubEnv("DATABASE_URL", undefined);
    expect(() => createContext()).not.toThrow();
  });
});
