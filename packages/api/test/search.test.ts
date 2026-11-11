import { afterEach, describe, expect, test, vi } from "vitest";

import { appRouter } from "../src/router";
import { httpSearchClient, SearchError, type SearchClient } from "../src/search";
import { createCallerFactory, createContext } from "../src/trpc";
import { memoryRepo } from "../src/repo";

const talkRow = (o: Record<string, unknown> & { id: number }) => ({
  external_id: null, title: `Talk ${o.id}`, abstract: "", units: [], topics: [], type: null,
  is_invited: false, is_withdrawn: false, start: null, end: null, sort_order: null,
  presentation_location: null, author_ids: [], presenter_ids: [], publication_reference: null,
  funding_acknowledgement: null, team_acknowledgement: null, session_id: null, session_title: null,
  session_code: null, session_type: null, session_topics: [], building: null, room: null, ...o,
});
const pickRow = (candidate_id: number, o: Record<string, unknown> = {}) => ({
  for_talk_id: 0, candidate_id, score: 0.4, rank: 1, match: true, cross_domain: false,
  why: "Shares transient photocurrent with your work.", strongest_parallel: "your talk → this talk",
  shared_methods: ["transient photocurrent"], evidence: { hops: 1, path: ["your talk", "this talk"] },
  engine_id: "graphrag_v1", run_id: "graphrag_v1-x", contract_version: 1,
  candidate: talkRow({ id: candidate_id, units: ["DPOLY"], start: "2026-03-18T19:24:00.000Z" }),
  ...o,
});
const QUERY = "I study exciton transport in porphyrin films with transient photocurrent.";
const RESULT = {
  anchor: talkRow({ id: 0, title: QUERY, abstract: QUERY }),
  picks: [pickRow(2802), pickRow(1600000000, { rank: 2, cross_domain: true, candidate: talkRow({
    id: 1600000000, type: "preprint:arxiv", external_id: "arXiv:2511.01234" }) })],
};

const fake = (impl: SearchClient["recommend"]): SearchClient => ({
  recommend: vi.fn(impl), themes: vi.fn(async () => ({})), ask: vi.fn(async () => ({})),
});
const call = (search?: SearchClient) =>
  createCallerFactory(appRouter)({ repo: memoryRepo([], []), engineId: "graph_v1", search });

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("search.recommend", () => {
  test("returns the query as the anchor and the service's picks, in the PicksResponse shape", async () => {
    const client = fake(async () => RESULT);
    const r = await call(client).search.recommend({ text: `  ${QUERY}  ` });
    expect(client.recommend).toHaveBeenCalledWith(QUERY);
    expect(r.presenter_id).toBeNull();
    expect(r.anchors.map((a) => a.title)).toEqual([QUERY]);
    expect(r.recommendations.map((p) => [p.candidate_id, p.cross_domain])).toEqual([
      [2802, false], [1600000000, true]]);
    expect(r.recommendations[1]?.candidate.type).toBe("preprint:arxiv");
  });

  test("rejects a query that is too short before calling the service", async () => {
    const client = fake(async () => RESULT);
    await expect(call(client).search.recommend({ text: "hi" })).rejects.toMatchObject({ code: "BAD_REQUEST" });
    expect(client.recommend).not.toHaveBeenCalled();
  });

  test("is SERVICE_UNAVAILABLE when no search service is configured or reachable", async () => {
    await expect(call().search.recommend({ text: QUERY })).rejects.toMatchObject({ code: "SERVICE_UNAVAILABLE" });
    const down = fake(async () => { throw new SearchError("unavailable", "connection refused"); });
    await expect(call(down).search.recommend({ text: QUERY })).rejects.toMatchObject({ code: "SERVICE_UNAVAILABLE" });
  });

  test("passes the service's own validation message through as BAD_REQUEST", async () => {
    const picky = fake(async () => { throw new SearchError("bad_request", "describe your research"); });
    await expect(call(picky).search.recommend({ text: QUERY })).rejects.toMatchObject({
      code: "BAD_REQUEST", message: "describe your research" });
  });

  test("rejects rows that break the contract", async () => {
    const broken = fake(async () => ({ ...RESULT, picks: [pickRow(1, { score: 7 })] }));
    await expect(call(broken).search.recommend({ text: QUERY })).rejects.toMatchObject({ code: "INTERNAL_SERVER_ERROR" });
  });
});

describe("httpSearchClient", () => {
  test("POSTs the text as JSON to <url>/recommend and returns the body", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(RESULT), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const out = await httpSearchClient("http://127.0.0.1:8765/").recommend(QUERY);
    expect(out).toEqual(RESULT);
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8765/recommend", expect.objectContaining({
      method: "POST", body: JSON.stringify({ text: QUERY }) }));
  });

  test("maps a 400 to bad_request with the service message, and network failure to unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ error: "too short" }), { status: 400 })));
    await expect(httpSearchClient("http://x").recommend(QUERY)).rejects.toMatchObject({ kind: "bad_request", message: "too short" });
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("fetch failed"); }));
    await expect(httpSearchClient("http://x").recommend(QUERY)).rejects.toMatchObject({ kind: "unavailable" });
  });
});

describe("createContext", () => {
  test("wires the search client to SEARCH_URL, defaulting to the local service", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(RESULT), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await createContext().search?.recommend(QUERY);
    expect(fetchMock.mock.calls[0]?.[0]).toBe("http://127.0.0.1:8765/recommend");
    vi.stubEnv("SEARCH_URL", "http://search.local:9000");
    await createContext().search?.recommend(QUERY);
    expect(fetchMock.mock.calls[1]?.[0]).toBe("http://search.local:9000/recommend");
  });
});
