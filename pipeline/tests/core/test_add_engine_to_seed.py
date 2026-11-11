"""scripts/add_engine_to_seed.py: run any registered engine over the talks of an
existing app seed and write a new seed holding BOTH the original rows and the
new engine's rows, so the web app can serve either via ENGINE_ID."""
import importlib.util
import json
from pathlib import Path

from gps_core.contracts import validate
from gps_engines.graphrag_v1.engine import GraphRAGEngine

spec = importlib.util.spec_from_file_location(
    "add_engine_to_seed",
    Path(__file__).resolve().parents[2] / "scripts" / "add_engine_to_seed.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIXTURE = Path(__file__).resolve().parents[3] / "apps/web/e2e/fixtures/app_seed.v2.json"


def test_seed_keeps_old_rows_and_adds_the_new_engine(tmp_path):
    old = json.loads(FIXTURE.read_text())
    engine = GraphRAGEngine(llm=None, models={}, workers=1)
    seed = mod.add_engine(engine, FIXTURE, tmp_path / "work", tmp_path / "seed.json")

    written = json.loads((tmp_path / "seed.json").read_text())
    assert written == seed
    assert len(seed["talks"]) == len(old["talks"]) and seed["locations"] == old["locations"]

    engines = {r["engine_id"] for r in seed["recommendations"]}
    assert engines == {"graph_v1", "graphrag_v1"}
    kept = [r for r in seed["recommendations"] if r["engine_id"] == "graph_v1"]
    assert kept == old["recommendations"]

    new = [r for r in seed["recommendations"] if r["engine_id"] == "graphrag_v1"]
    assert any(r["match"] for r in new)
    assert {r["for_talk_id"] for r in new} == {0}            # the seed's anchor talk
    assert 0 not in {r["candidate_id"] for r in new}         # never itself
    talk_ids = {t["id"] for t in seed["talks"]}
    assert {r["candidate_id"] for r in new} <= talk_ids      # referential integrity
    for r in new:
        validate("recommendation", r)
    assert {m["engine_id"] for m in seed["runs"]} == {"graph_v1", "graphrag_v1"}


def test_rerun_replaces_rather_than_duplicates_the_engine_rows(tmp_path):
    engine = GraphRAGEngine(llm=None, models={}, workers=1)
    first = mod.add_engine(engine, FIXTURE, tmp_path / "work", tmp_path / "a.json")
    again = mod.add_engine(engine, tmp_path / "a.json", tmp_path / "work", tmp_path / "b.json")
    count = lambda s: sum(r["engine_id"] == "graphrag_v1" for r in s["recommendations"])  # noqa: E731
    assert count(again) == count(first)
    assert sum(m["engine_id"] == "graphrag_v1" for m in again["runs"]) == 1


def test_extra_papers_join_the_corpus_and_can_be_recommended(tmp_path):
    """Preprints (out/preprints.json from fetch_preprints.py) are candidates too."""
    from xml.sax.saxutils import escape

    from gps_data.preprints import parse_arxiv
    from gps_data.talk import to_row
    anchor = next(t for t in json.loads(FIXTURE.read_text())["talks"] if t["id"] == 0)
    paper = parse_arxiv(
        '<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
        "<id>http://arxiv.org/abs/2511.00001v1</id><published>2025-11-01T00:00:00Z</published>"
        f"<title>{escape(anchor['title'])} revisited</title><summary>{escape(anchor['abstract'])}</summary>"
        '<arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cond-mat.mtrl-sci"/>'
        "</entry></feed>")[0]
    extra = tmp_path / "preprints.json"
    extra.write_text(json.dumps({"talks": [to_row(paper)]}))

    engine = GraphRAGEngine(llm=None, models={}, workers=1)
    seed = mod.add_engine(engine, FIXTURE, tmp_path / "work", tmp_path / "seed.json",
                          extra=[extra])
    assert paper.id in {t["id"] for t in seed["talks"]}
    rec = next(r for r in seed["recommendations"]
               if r["engine_id"] == "graphrag_v1" and r["candidate_id"] == paper.id)
    assert rec["match"]
