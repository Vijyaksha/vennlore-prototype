"""graphrag_v1 extras beyond the Engine protocol: research themes and questions about the
whole conference (GraphRAG global search), answered only from theme summaries."""
from gps_engines.graphrag_v1.engine import GraphRAGEngine

from .fakes import ExhaustedLLM, RoutingFakeLLM, corpus


def make(llm):
    models = {"extract": "fake", "themes": "fake", "explain": "fake"} if llm else {}
    return GraphRAGEngine(llm=llm, models=models, workers=1)


def test_themes_lists_every_theme_with_its_talks(tmp_path):
    e = make(RoutingFakeLLM())
    art = e.index(corpus(), tmp_path)
    themes = e.themes(art)
    assert themes and all({"id", "title", "summary", "concepts", "talk_ids"} <= t.keys() for t in themes)
    assert {i for t in themes for i in t["talk_ids"]} <= {2, 3, 4, 5}


def test_ask_ranks_related_themes_and_answers_from_them_only(tmp_path):
    llm = RoutingFakeLLM()
    e = make(llm)
    art = e.index(corpus(), tmp_path)
    out = e.ask(art, "Which talks measure transient photocurrent?")
    assert out["answer"] == "Grounded answer from the listed themes."
    assert out["theme_ids"] and len(out["theme_ids"]) <= 3
    first = next(t for t in e.themes(art) if t["id"] == out["theme_ids"][0])
    assert "transient photocurrent" in first["concepts"]
    prompt = next(p for p in llm.prompts if "Answer the question using ONLY" in p)
    assert "Which talks measure transient photocurrent?" in prompt


def test_ask_without_an_llm_returns_ranked_themes_and_no_answer(tmp_path):
    e = make(None)
    art = e.index(corpus(), tmp_path)
    out = e.ask(art, "gravitational waves and neutron stars")
    assert out["answer"] is None and out["theme_ids"]


def test_ask_reuses_a_saved_answer(tmp_path):
    e = make(RoutingFakeLLM())
    art = e.index(corpus(), tmp_path)
    e.ask(art, "Which talks measure transient photocurrent?")
    again = make(ExhaustedLLM())          # would fail the test if it called the LLM
    assert again.ask(art, "Which talks measure transient photocurrent?")["answer"]


def test_theme_concepts_are_listed_once_even_when_a_topic_and_method_share_a_name(tmp_path):
    from dataclasses import replace
    talks = [replace(t, topics=t.topics + ("self-assembly",)) for t in corpus()]
    e = make(RoutingFakeLLM())
    for theme in e.themes(e.index(talks, tmp_path)):
        assert len(theme["concepts"]) == len(set(theme["concepts"]))


def test_ask_ranks_by_meaning_words_and_the_themes_talks(tmp_path):
    """'learning' inside 'machine learning' must not pull in an unrelated theme by spelling;
    the theme whose talks are about the question's subject comes first."""
    e = make(None)
    art = e.index(corpus(), tmp_path)
    out = e.ask(art, "Which talks search for gravitational waves from neutron stars?")
    first = next(t for t in e.themes(art) if t["id"] == out["theme_ids"][0])
    assert 4 in first["talk_ids"]


def test_ask_finds_the_gravitational_wave_theme_in_the_real_programme(tmp_path):
    """On Rupert's 58 sample talks, a gravitational-wave question must lead with a theme
    whose talks are gravitational-wave talks (units DGRAV), not a theme that only shares letters."""
    import json
    from pathlib import Path

    from gps_data.talk import from_row
    seed = Path(__file__).resolve().parents[3] / "apps/web/e2e/fixtures/app_seed.v2.json"
    talks = [from_row(t) for t in json.loads(seed.read_text())["talks"]]
    units = {t.id: t.units for t in talks}
    e = make(None)
    art = e.index(talks, tmp_path)
    out = e.ask(art, "gravitational wave data analysis")
    first = next(t for t in e.themes(art) if t["id"] == out["theme_ids"][0])
    assert any("DGRAV" in units[i] for i in first["talk_ids"])
