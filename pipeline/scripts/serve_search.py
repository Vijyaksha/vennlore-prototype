"""Free-text search over an engine's index, served on localhost for the web app.

  ENGINE=graphrag_v1 uv run python scripts/serve_search.py                  # fast: no LLM per query
  ENGINE=graphrag_v1 ENGINE_CONFIG='{"provider": "local"}' uv run python scripts/serve_search.py
                                                                            # LLM-written reasons (slower)
  POST /recommend {"text": "<your research>"}  ->  {"anchor": Talk, "picks": [Recommendation + candidate Talk]}
  GET  /themes                                  ->  themes_response (contract)
  POST /ask {"question": "..."}                 ->  ask_response (contract): LLM answer when configured
  GET  /health

The query becomes an external anchor (Talk id 0). Rows go through core's run_recommend,
so they are validated against the contract and saved under <index>/queries/. Only match=true
rows are returned, joined with their candidate Talk from the seed (talks + papers).
Defaults: --index out/<engine>/seed/index, --seed out/app_seed.v2.json, port 8765."""
import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gps_core.checkpoint import content_key  # noqa: E402
from gps_core.contracts import ContractError, validate  # noqa: E402
from gps_core.protocol import Engine, IndexArtifact  # noqa: E402
from gps_core.registry import engine_from_env, get_engine  # noqa: E402
from gps_core.run import run_recommend  # noqa: E402
from gps_data.talk import external_anchor, to_row  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out"
MIN_CHARS, MAX_CHARS = 10, 4000


def short_title(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


class Searcher:
    def __init__(self, engine: Engine, index_path: Path, talks: dict[int, dict],
                 ask_engine: Engine | None = None):
        self.engine, self.talks = engine, talks
        self.ask_engine = ask_engine or engine   # e.g. an LLM-backed copy, so search stays fast
        self.index = IndexArtifact(path=Path(index_path), engine_id=engine.id)
        self._lock = threading.Lock()   # one query at a time: a local LLM serves one anyway

    def search(self, text: str) -> dict:
        text = " ".join(str(text).split())
        if not MIN_CHARS <= len(text) <= MAX_CHARS:
            raise ValueError(f"describe your research in at least {MIN_CHARS} and at most "
                             f"{MAX_CHARS} characters")
        anchor = external_anchor(short_title(text), text, [])
        out = self.index.path / "queries" / content_key("search", text)
        with self._lock:
            rows, _ = run_recommend(self.engine, anchor, self.index, out)
        picks = [{**r.to_row(), "candidate": self.talks[r.candidate_id]}
                 for r in rows if r.match and r.candidate_id in self.talks]
        return {"anchor": to_row(anchor), "picks": picks}

    def _theme_row(self, t: dict) -> dict:
        talks = [{"id": i, "title": self.talks[i]["title"], "type": self.talks[i].get("type")}
                 for i in t["talk_ids"] if i in self.talks]
        return {"id": t["id"], "title": t["title"], "summary": t["summary"],
                "concepts": list(t["concepts"]), "talks": talks}

    def themes(self) -> dict:
        """Research themes, for engines that have them (contract: themes_response)."""
        if not hasattr(self.engine, "themes"):
            raise LookupError(f"engine {self.engine.id} has no research themes")
        out = {"engine_id": self.engine.id,
               "themes": [self._theme_row(t) for t in self.engine.themes(self.index)]}
        validate("themes_response", out)
        return out

    def ask(self, question: str) -> dict:
        """A question about the whole conference, answered from themes (contract: ask_response)."""
        question = " ".join(str(question).split())
        if not 3 <= len(question) <= 1000:
            raise ValueError("ask a question of 3 to 1000 characters")
        if not hasattr(self.ask_engine, "ask"):
            raise LookupError(f"engine {self.engine.id} cannot answer questions")
        with self._lock:
            res = self.ask_engine.ask(self.index, question)
        by_id = {t["id"]: t for t in self.engine.themes(self.index)}
        out = {"engine_id": self.engine.id, "question": question, "answer": res["answer"],
               "themes": [self._theme_row(by_id[i]) for i in res["theme_ids"] if i in by_id]}
        validate("ask_response", out)
        return out


def make_server(searcher: Searcher, port: int = 8765, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: dict) -> None:
            data = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                return self._send(200, {"ok": True, "engine_id": searcher.engine.id})
            if self.path == "/themes":
                return self._handle(searcher.themes)
            self._send(404, {"error": "not found"})

        def do_POST(self):
            routes = {"/recommend": ("text", searcher.search), "/ask": ("question", searcher.ask)}
            if self.path not in routes:
                return self._send(404, {"error": "not found"})
            field, fn = routes[self.path]
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            except json.JSONDecodeError as e:
                return self._send(400, {"error": str(e)})
            self._handle(lambda: fn(body.get(field, "")))

        def _handle(self, fn):
            try:
                self._send(200, fn())
            except ContractError as e:   # our own output broke the contract: a server error
                print(f"[search] contract violation: {e}", flush=True)
                self._send(500, {"error": str(e)})
            except ValueError as e:
                self._send(400, {"error": str(e)})
            except LookupError as e:
                self._send(404, {"error": str(e)})
            except Exception as e:   # surfaced to the API as a 502, logged here
                print(f"[search] failed: {type(e).__name__}: {e}", flush=True)
                self._send(500, {"error": f"{type(e).__name__}: {e}"})

        def log_message(self, fmt, *args):
            print("[search] " + fmt % args, flush=True)

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    engine = engine_from_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=str(OUT / engine.id / "seed" / "index"))
    ap.add_argument("--seed", default=str(OUT / "app_seed.v2.json"))
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--ask-llm", default=None,
                    help="provider for written answers in Ask (e.g. local = LM Studio); search stays fast")
    a = ap.parse_args()
    if not (Path(a.index) / "index.json").exists():
        raise SystemExit(f"no index at {a.index}: run scripts/add_engine_to_seed.py first")
    talks = {t["id"]: t for t in json.loads(Path(a.seed).read_text(encoding="utf-8"))["talks"]}
    ask_engine = get_engine(engine.id, provider=a.ask_llm) if a.ask_llm else None
    server = make_server(Searcher(engine, Path(a.index), talks, ask_engine), port=a.port)
    print(f"[search] {engine.id} over {len(talks)} talks and papers on http://127.0.0.1:{a.port}",
          flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
