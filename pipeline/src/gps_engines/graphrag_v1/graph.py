"""The knowledge graph and its research themes.

Talk -- topic   (the programme's own topic labels, Talk.topics)
Talk -- method  (LLM-extracted from title + abstract)
Talk -- unit    (APS division, Talk.units: the "track")
Talk -- concept (rel "mentions"): any method or topic its title/abstract names, so papers
                 and talks connect even when their labels come from different vocabularies

Themes are Louvain communities of the concept co-occurrence graph: concepts
that talks use together. Pure functions over plain dicts so they serialise
straight into index.json."""
import math
import re

import networkx as nx
from networkx.algorithms.community import louvain_communities

LOUVAIN_SEED = 7
THEME_RESOLUTION = 1.3       # above 1 favours tighter, more specific themes


def norm(label: str) -> str:
    """Casefold, collapse spaces, trim punctuation: one spelling per concept."""
    label = " ".join(str(label).casefold().split())
    return label.strip(" .,;:-*\"'()[]")


def clean_methods(raw, limit: int = 8) -> list[str]:
    """Short, unique, normalised method names from whatever the LLM returned."""
    out: list[str] = []
    for m in raw if isinstance(raw, list) else []:
        m = norm(m)
        if 2 < len(m) <= 60 and len(m.split()) <= 6 and m not in out:
            out.append(m)
    return out[:limit]


_PAREN = re.compile(r"\([^)]*\)")


def method_key(label: str) -> tuple[str, ...]:
    """Spelling-insensitive identity of a method: no parentheticals or punctuation,
    singular words. 'Photoluminescence (PL) spectroscopy' == 'photoluminescence spectroscopy'."""
    words = _WORD.findall(_PAREN.sub(" ", label.casefold()))
    return tuple(w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w
                 for w in words)


def merge_methods(talks: list[dict]) -> None:
    """Near-duplicate method names become one node, named by their most used spelling,
    so small-model spelling drift does not split the graph."""
    counts: dict[str, int] = {}
    for t in talks:
        for m in t["methods"]:
            counts[m] = counts.get(m, 0) + 1
    best: dict[tuple, str] = {}
    for m, c in sorted(counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0])):
        best.setdefault(method_key(m), m)
    for t in talks:
        t["methods"] = list(dict.fromkeys(best[method_key(m)] for m in t["methods"]))


def merge_plurals(talks: list[dict]) -> None:
    """'transient photocurrents' and 'transient photocurrent' become one node,
    so small-model spelling drift does not split the graph."""
    seen = {m for t in talks for m in t["methods"]}
    for t in talks:
        t["methods"] = list(dict.fromkeys(
            m[:-1] if m.endswith("s") and m[:-1] in seen else m for m in t["methods"]))


def concepts_of(t: dict) -> list[tuple[str, str]]:
    """(kind, label) pairs for a talk dict from index.json."""
    return [("method", m) for m in t["methods"]] + [("topic", norm(x)) for x in t["topics"]]


MENTION_WEIGHT = 0.5      # a concept named in the abstract counts half a declared one


def build_graph(talks: list[dict]) -> nx.Graph:
    g = nx.Graph()
    for t in talks:
        tid = f"talk:{t['id']}"
        g.add_node(tid, kind="talk")
        for u in t["units"]:
            g.add_edge(tid, f"unit:{u}", rel="in_unit")
            g.nodes[f"unit:{u}"]["kind"] = "unit"
        for kind, label in concepts_of(t):
            g.add_edge(tid, f"{kind}:{label}", rel="uses" if kind == "method" else "about", w=1.0)
            g.nodes[f"{kind}:{label}"].update(kind=kind, label=label)
    add_mention_edges(g, talks)
    return g


def add_mention_edges(g: nx.Graph, talks: list[dict], max_words: int = 6) -> None:
    """Link each talk to every known concept its title or abstract names (whole words,
    plural-tolerant). One pass per talk over its word n-grams, so it scales to thousands.
    Words many abstracts use ('learning', 'dynamics') are noise as mentions, not bridges:
    a concept links by mention only if few documents mention it. Such concepts are
    marked common=True so queries do not seed on them either."""
    by_key: dict[tuple, str] = {}
    for c, d in g.nodes(data=True):
        if d["kind"] in ("method", "topic") and len(d["label"]) >= 4:
            by_key.setdefault(method_key(d["label"]), c)
    if not by_key:
        return
    hits: dict[str, set[str]] = {}
    for t in talks:
        words = method_key(f"{t['title']} {t['abstract']}")
        grams = {words[i:i + k] for k in range(1, max_words + 1) for i in range(len(words) - k + 1)}
        for key in grams & by_key.keys():
            hits.setdefault(by_key[key], set()).add(f"talk:{t['id']}")
    n = len(talks)
    for c, tids in hits.items():
        limit = max(5, (0.05 if len(method_key(g.nodes[c]["label"])) > 1 else 0.02) * n)
        if len(tids) > limit:
            g.nodes[c]["common"] = True
            continue
        for tid in tids:
            if not g.has_edge(tid, c):
                g.add_edge(tid, c, rel="mentions", w=MENTION_WEIGHT)


def idf(g: nx.Graph, n_talks: int) -> dict[str, float]:
    """Rarer concepts carry more evidence: smoothed inverse document frequency."""
    return {c: math.log((n_talks + 1) / (g.degree(c) + 1)) + 1
            for c, d in g.nodes(data=True) if d["kind"] in ("method", "topic")}


def is_generic(g: nx.Graph, concept: str, n_talks: int) -> bool:
    """A concept most of the programme shares cannot make a pick surprising."""
    return g.degree(concept) > max(3, 0.3 * n_talks)


def detect_themes(g: nx.Graph) -> list[dict]:
    """Generic concepts (shared by much of the programme) are left out, so they cannot
    glue unrelated talks into one giant theme."""
    n_talks = sum(1 for _, d in g.nodes(data=True) if d["kind"] == "talk")
    cg = nx.Graph()
    for t, d in g.nodes(data=True):
        if d["kind"] != "talk":
            continue
        cs = sorted(n for n in g.neighbors(t) if g.nodes[n]["kind"] in ("method", "topic")
                    and not is_generic(g, n, n_talks))
        for i, a in enumerate(cs):
            cg.add_node(a)
            for b in cs[i + 1:]:
                w = cg.get_edge_data(a, b, {"weight": 0})["weight"]
                cg.add_edge(a, b, weight=w + 1)
    if cg.number_of_nodes() == 0:
        return []
    groups = louvain_communities(cg, weight="weight", resolution=THEME_RESOLUTION, seed=LOUVAIN_SEED)
    groups = sorted(groups, key=lambda s: (-len(s), sorted(s)))
    themes = []
    for i, nodes in enumerate(groups):
        ordered = sorted(nodes, key=lambda n: (-g.degree(n), n))
        talk_ids = sorted({int(t.split(":")[1]) for n in nodes for t in g.neighbors(n)
                           if g.nodes[t]["kind"] == "talk"})
        themes.append({"id": f"T{i + 1}", "concepts": list(dict.fromkeys(g.nodes[n]["label"] for n in ordered)),
                       "talk_ids": talk_ids})
    return themes


def fallback_theme_text(theme: dict) -> dict:
    return {"title": " / ".join(theme["concepts"][:3]).title(),
            "summary": "Talks connected by " + ", ".join(theme["concepts"][:6]) + "."}


def theme_of(talk: dict, themes: list[dict]) -> str:
    """Title of the theme sharing the most concepts with the talk ('' if none)."""
    labels = {label for _, label in concepts_of(talk)}
    best = max(themes, key=lambda th: (len(labels & set(th["concepts"])), -int(th["id"][1:])),
               default=None)
    return best["title"] if best and labels & set(best["concepts"]) else ""


_WORD = re.compile(r"[a-z0-9]+")


def mentions(text: str, label: str) -> bool:
    """Does free text mention a concept label (whole words, plural-tolerant)?"""
    words = _WORD.findall(text.casefold())
    target = _WORD.findall(label.casefold())
    if not target:
        return False
    stem = lambda w: w[:-1] if len(w) > 3 and w.endswith("s") else w
    words, target = [stem(w) for w in words], [stem(w) for w in target]
    k = len(target)
    return any(words[i:i + k] == target for i in range(len(words) - k + 1))
