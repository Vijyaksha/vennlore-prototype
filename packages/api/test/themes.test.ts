import { afterEach, describe, expect, test, vi } from "vitest";

import { appRouter } from "../src/router";
import { httpSearchClient, SearchError, type SearchClient } from "../src/search";
import { createCallerFactory } from "../src/trpc";
import { memoryRepo } from "../src/repo";

const THEME = {
  id: "T1", title: "Light-driven charge transport", summary: "Read out charge with light.",
  concepts: ["transient photocurrent"], talks: [{ id: 2802, title: "Memristive DNA devices", type: null }],
};
const THEMES = { engine_id: "graphrag_v1", themes: [THEME] };
const ASK = { engine_id: "graphrag_v1", question: "Which themes use light?", answer: "Light-driven charge transport.", themes: [THEME] };

const client = (o: Partial<SearchClient> = {}): SearchClient => ({
  recommend: vi.fn(async () => ({ anchor: {}, picks: [] })),
  themes: vi.fn(async () => THEMES),
  ask: vi.fn(async () => ASK),
  ...o,
});
const call = (search?: SearchClient) =>
  createCallerFactory(appRouter)({ repo: memoryRepo([], []), engineId: "graph_v1", search });

afterEach(() => vi.unstubAllGlobals());

describe("themes.list", () => {
  test("returns the engine's research themes in the ThemesResponse shape", async () => {
    const r = await call(client()).themes.list();
    expect(r.themes.map((t) => t.title)).toEqual(["Light-driven charge transport"]);
  });
  test("is SERVICE_UNAVAILABLE without a search service", async () => {
    await expect(call().themes.list()).rejects.toMatchObject({ code: "SERVICE_UNAVAILABLE" });
  });
  test("rejects themes that break the contract", async () => {
    const bad = client({ themes: vi.fn(async () => ({ engine_id: "graphrag_v1", themes: [{ id: "T1" }] })) });
    await expect(call(bad).themes.list()).rejects.toMatchObject({ code: "INTERNAL_SERVER_ERROR" });
  });
});

describe("themes.ask", () => {
  test("forwards the trimmed question and returns the AskResponse", async () => {
    const c = client();
    const r = await call(c).themes.ask({ question: "  Which themes use light?  " });
    expect(c.ask).toHaveBeenCalledWith("Which themes use light?");
    expect(r.answer).toBe("Light-driven charge transport.");
    expect(r.themes[0]?.id).toBe("T1");
  });
  test("rejects an empty question before calling the service", async () => {
    const c = client();
    await expect(call(c).themes.ask({ question: " " })).rejects.toMatchObject({ code: "BAD_REQUEST" });
    expect(c.ask).not.toHaveBeenCalled();
  });
  test("maps a service outage to SERVICE_UNAVAILABLE", async () => {
    const down = client({ ask: vi.fn(async () => { throw new SearchError("unavailable", "refused"); }) });
    await expect(call(down).themes.ask({ question: "Which themes?" })).rejects.toMatchObject({ code: "SERVICE_UNAVAILABLE" });
  });
});

describe("httpSearchClient themes and ask", () => {
  test("GETs /themes and POSTs /ask", async () => {
    const fetchMock = vi.fn<typeof fetch>(async (url) =>
      new Response(JSON.stringify(String(url).endsWith("/themes") ? THEMES : ASK), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const c = httpSearchClient("http://127.0.0.1:8765");
    expect(await c.themes()).toEqual(THEMES);
    expect(await c.ask("Which themes use light?")).toEqual(ASK);
    expect(fetchMock.mock.calls[0]?.[0]).toBe("http://127.0.0.1:8765/themes");
    expect(fetchMock.mock.calls[1]?.[0]).toBe("http://127.0.0.1:8765/ask");
    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({ method: "POST", body: JSON.stringify({ question: "Which themes use light?" }) });
  });
});
