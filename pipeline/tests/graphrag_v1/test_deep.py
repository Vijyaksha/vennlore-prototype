"""Deeper GraphRAG: mention edges, method merging, multi-hop walks, finer themes."""
from dataclasses import replace

from gps_data.talk import external_anchor
from gps_engines.graphrag_v1.engine import GraphRAGEngine
from gps_engines.graphrag_v1.graph import build_graph, merge_methods

from .fakes import RoutingFakeLLM


def t(id, title, abstract, units, topics=()):
    return replace(external_anchor(title, abstract, list(units)), id=id, topics=tuple(topics))


def test_a_paper_links_to_methods_its_abstract_mentions():
    talks = [
        {"id": 1, "title": "Exciton films", "abstract": "We study films.", "units": ["DPOLY"],
         "topics": [], "methods": ["transient photocurrent"]},
        {"id": 2, "title": "A preprint", "units": ["arXiv:cs.LG"], "topics": ["cs.LG"], "methods": [],
         "abstract": "We fit transient photocurrent traces with neural networks."},
    ]
    g = build_graph(talks)
    assert "talk:2" in set(g.neighbors("method:transient photocurrent"))
    assert g.edges["talk:2", "method:transient photocurrent"]["rel"] == "mentions"


def test_near_duplicate_methods_merge_into_the_most_used_name():
    talks = [{"methods": ["photoluminescence spectroscopy"]},
             {"methods": ["photoluminescence spectroscopy"]},
             {"methods": ["photoluminescence (pl) spectroscopy", "x-ray diffraction"]}]
    merge_methods(talks)
    assert talks[2]["methods"] == ["photoluminescence spectroscopy", "x-ray diffraction"]


# A chain the old 3-hop walk cannot reach:
#   your talk -A-> T1 (div X) -B-> T2 (div Y) -C-> T3 (div Z)
CHAIN = {
    "Anchor": ["method a"], "Talk one": ["method a", "method b"],
    "Talk two": ["method b", "method c"], "Talk three": ["method c"],
    "Noise": ["method z"],
}


def chain():
    return [t(1, "Talk one", "First study.", ["X"]), t(2, "Talk two", "Second study.", ["Y"]),
            t(3, "Talk three", "Third study.", ["Z"]), t(4, "Noise", "Unrelated.", ["W"])]


def run_chain(tmp_path):
    e = GraphRAGEngine(llm=RoutingFakeLLM(methods=CHAIN), workers=1,
                       models={"extract": "f", "themes": "f", "explain": "f"})
    art = e.index(chain(), tmp_path)
    rows = e.recommend(t(0, "Anchor", "My study.", ["X"]), art)
    return {r.candidate_id: r for r in rows}


def test_multi_hop_walk_reaches_talks_beyond_three_hops(tmp_path):
    rows = run_chain(tmp_path)
    deep = rows[3]
    assert deep.match and deep.cross_domain
    assert deep.evidence["hops"] >= 5
    path = deep.evidence["path"]
    assert path[0] == "your talk" and path[-1] == "this talk"
    assert "method: method a" in path and "method: method c" in path
    assert '"Talk two"' in path


def test_unconnected_talk_is_still_not_recommended(tmp_path):
    rows = run_chain(tmp_path)
    assert 4 not in rows or not rows[4].match


def test_generic_topics_do_not_glue_themes_together(tmp_path):
    talks = [t(i, f"Talk {i}", "Study.", [u], ["physics", topic])
             for i, (u, topic) in enumerate([("A", "optics"), ("A", "optics"), ("B", "magnetism"),
                                             ("B", "magnetism"), ("C", "plasma"), ("C", "plasma")], 1)]
    e = GraphRAGEngine(llm=None, models={}, workers=1)
    themes = e.themes(e.index(talks, tmp_path))
    assert len(themes) >= 3
    assert all("physics" not in th["concepts"] for th in themes)


def test_common_single_words_do_not_link_by_mention():
    """'learning' appears in many abstracts: as a mention it is noise, not a bridge.
    A rare specific term ('photoconductivity') still links."""
    talks = [{"id": 0, "title": "Physics education", "abstract": "Active learning in class.",
              "units": ["FED"], "topics": ["learning", "photoconductivity"], "methods": []}]
    talks += [{"id": i, "title": f"ML paper {i}", "abstract": "Deep learning for images.",
               "units": ["arXiv:cs.LG"], "topics": [], "methods": []} for i in range(1, 60)]
    talks += [{"id": 99, "title": "Nanorods", "abstract": "We measure photoconductivity.",
               "units": ["DPOLY"], "topics": [], "methods": []}]
    g = build_graph(talks)
    assert not g.has_edge("talk:1", "topic:learning")
    assert g.has_edge("talk:99", "topic:photoconductivity")


def test_repeated_searches_reuse_the_loaded_index(tmp_path, monkeypatch):
    """The graph and text index are built once per index, not once per search."""
    from gps_engines.graphrag_v1 import engine as eng
    e = GraphRAGEngine(llm=None, models={}, workers=1)
    art = e.index(chain(), tmp_path)
    builds = []
    real = eng.build_graph
    monkeypatch.setattr(eng, "build_graph", lambda talks: builds.append(1) or real(talks))
    first = e.recommend(t(0, "Anchor", "My study.", ["X"]), art)
    second = e.recommend(t(0, "Anchor", "My study.", ["X"]), art)
    assert len(builds) == 1
    assert [r.candidate_id for r in first] == [r.candidate_id for r in second]
