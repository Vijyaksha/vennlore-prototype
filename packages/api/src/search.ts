/** Search, research themes and conference questions live in the pipeline
 *  (pipeline/scripts/serve_search.py), which runs an engine over its index. The API only
 *  forwards requests and validates every response against the contract
 *  (PicksResponseSchema, ThemesResponseSchema, AskResponseSchema). */
export interface SearchResult {
  anchor: unknown;
  picks: unknown[];
}

export interface SearchClient {
  recommend(text: string): Promise<SearchResult>;
  themes(): Promise<unknown>;
  ask(question: string): Promise<unknown>;
}

export class SearchError extends Error {
  constructor(
    readonly kind: "unavailable" | "bad_request" | "failed",
    message: string,
  ) {
    super(message);
    this.name = "SearchError";
  }
}

export const DEFAULT_SEARCH_URL = "http://127.0.0.1:8765";

/** Client over the pipeline's local HTTP service. */
export function httpSearchClient(baseUrl: string): SearchClient {
  const base = baseUrl.replace(/\/+$/, "");

  async function request(path: string, body?: unknown): Promise<unknown> {
    let res: Response;
    try {
      res = await fetch(`${base}${path}`, body === undefined ? { method: "GET" } : {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (error) {
      throw new SearchError("unavailable", `search service unreachable: ${String(error)}`);
    }
    const json = (await res.json().catch(() => ({}))) as { error?: string };
    if (res.status === 400) throw new SearchError("bad_request", json.error ?? "bad request");
    if (res.status === 404) throw new SearchError("unavailable", json.error ?? "not available for this engine");
    if (!res.ok) throw new SearchError("failed", json.error ?? `search service failed (${res.status})`);
    return json;
  }

  return {
    recommend: async (text) => (await request("/recommend", { text })) as SearchResult,
    themes: () => request("/themes"),
    ask: (question) => request("/ask", { question }),
  };
}
