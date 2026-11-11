"""scripts/serve_search.py: free-text search over an engine's index. Every row goes
through core's run_recommend (validated against the contract) and comes back
joined with its candidate Talk, in the web app's Pick shape."""
import importlib.util
import json
import threading
import urllib.request
from pathlib import Path

from graphrag_v1.fakes import corpus

from gps_core.contracts import validate
from gps_core.run import run_index
from gps_data.talk import to_row
from gps_engines.graphrag_v1.engine import GraphRAGEngine

spec = importlib.util.spec_from_file_location(
    "serve_search", Path(__file__).resolve().parents[2] / "scripts" / "serve_search.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

QUERY = ("I study exciton transport and photoconductivity in self-assembled porphyrin "
         "organic semiconductor films using transient photocurrent.")


def make_searcher(tmp_path):
    engine = GraphRAGEngine(llm=None, models={}, workers=1)
    art, _ = run_index(engine, corpus(), tmp_path / "index")
    talks = {t.id: to_row(t) for t in corpus()}
    return mod.Searcher(engine, art.path, talks)


def test_search_returns_contract_valid_picks_joined_with_talks(tmp_path):
    out = make_searcher(tmp_path).search(QUERY)
    validate("talk", out["anchor"])
    assert out["anchor"]["id"] == 0 and out["anchor"]["abstract"] == QUERY
    assert out["picks"], "the closest talk should match"
    for p in out["picks"]:
        cand = p.pop("candidate")
        validate("recommendation", p)
        validate("talk", cand)
        assert p["match"] and cand["id"] == p["candidate_id"]
    assert out["picks"][0]["candidate_id"] == 2


def test_anchor_title_is_a_short_version_of_the_query(tmp_path):
    long = "word " * 80
    out = make_searcher(tmp_path).search(long)
    assert len(out["anchor"]["title"]) <= 121 and out["anchor"]["title"].endswith("…")


def test_rejects_queries_that_are_too_short(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="at least"):
        make_searcher(tmp_path).search("hi")


def test_http_endpoint_serves_search_and_health(tmp_path):
    server = mod.make_server(make_searcher(tmp_path), port=0)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health") as r:
            assert json.loads(r.read())["ok"] is True
        req = urllib.request.Request(f"http://127.0.0.1:{port}/recommend",
                                     data=json.dumps({"text": QUERY}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            body = json.loads(r.read())
        assert body["picks"] and body["anchor"]["abstract"] == QUERY
        bad = urllib.request.Request(f"http://127.0.0.1:{port}/recommend",
                                     data=b'{"text": "hi"}',
                                     headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(bad)
            raise AssertionError("expected HTTP 400")
        except urllib.error.HTTPError as e:
            assert e.code == 400
    finally:
        server.shutdown()


def test_themes_are_contract_valid_and_name_their_talks(tmp_path):
    out = make_searcher(tmp_path).themes()
    validate("themes_response", out)
    assert out["engine_id"] == "graphrag_v1" and out["themes"]
    talk = out["themes"][0]["talks"][0]
    assert talk["title"] and "type" in talk


def test_ask_is_contract_valid_and_returns_ranked_themes(tmp_path):
    out = make_searcher(tmp_path).ask("Which talks measure transient photocurrent?")
    validate("ask_response", out)
    assert out["question"] == "Which talks measure transient photocurrent?"
    assert out["answer"] is None and out["themes"]          # no LLM in this searcher


def test_ask_rejects_an_empty_question(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="question"):
        make_searcher(tmp_path).ask("  ")


def test_http_serves_themes_and_ask(tmp_path):
    server = mod.make_server(make_searcher(tmp_path), port=0)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/themes") as r:
            assert json.loads(r.read())["themes"]
        req = urllib.request.Request(f"http://127.0.0.1:{port}/ask",
                                     data=json.dumps({"question": "gravitational waves?"}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            assert json.loads(r.read())["question"] == "gravitational waves?"
    finally:
        server.shutdown()


def test_ask_can_use_a_separate_llm_engine_while_search_stays_llm_free(tmp_path):
    from graphrag_v1.fakes import RoutingFakeLLM
    base = make_searcher(tmp_path)
    llm_engine = GraphRAGEngine(llm=RoutingFakeLLM(), models={"explain": "fake"}, workers=1)
    s = mod.Searcher(base.engine, base.index.path, base.talks, ask_engine=llm_engine)
    assert s.ask("Which talks measure transient photocurrent?")["answer"]
    assert s.engine.llm is None
