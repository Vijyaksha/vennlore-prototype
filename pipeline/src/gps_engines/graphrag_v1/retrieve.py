"""Local search over the graph: score every talk against the anchor, then
pick core (same division) and unexpected (other division) talks.

Unexpected talks are reached three ways, the strongest wins:
  direct   your talk -> shared method -> talk in another division
  3 hops   your talk -> strong match -> its method -> talk in another division
  deep     a Personalized PageRank walk over the whole graph, explained by the
           cheapest path (e.g. your talk -> method A -> "talk" -> method B -> this talk)
Retrieval decides WHAT is recommended; the LLM only explains it."""
from dataclasses import dataclass, field

import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from gps_engines.graphrag_v1.graph import concepts_of, idf, is_generic, method_key

MAX_CORE, MAX_UNEXPECTED = 2, 3     # the product's picks rail: 2 core + 3 unexpected
CORE_MIN = 0.10                     # absolute floor for a core pick
CORE_RELATIVE = 0.5                 # ...and at least half the best core score
UNEXPECTED_MIN = 0.06
SEEDS = 5                           # strongest talks a 3-hop walk may start from
KEEP_UNMATCHED = 8                  # near misses kept as match=False rows, for evaluation
BRIDGE_WEIGHT = {"method": 1.0, "topic": 0.6}
DEEP_WEIGHT = 0.5                   # a deep walk counts half a direct link at equal strength
DEEP_MAX_HOPS = 8
GENERIC_DAMPING = 0.1               # generic concepts barely conduct the walk


@dataclass
class Scored:
    talk: dict
    score: float = 0.0
    text: float = 0.0
    concept: float = 0.0
    shared: list[str] = field(default_factory=list)   # shared concept labels, methods first
    bridge: str = ""                                    # label of the strongest bridging concept
    bridge_kind: str = ""
    hops: int = 1
    via: dict | None = None                             # seed talk of a 3-hop walk
    deep: list[str] | None = None                       # full path of a deep walk
    deep_score: float = 0.0
    cross_domain: bool = False
    match: bool = False


def doc(t: dict) -> str:
    return " ".join([t["title"], t["abstract"], *t["topics"], *t["methods"]])


def anchor_concepts(anchor: dict, g: nx.Graph) -> set[str]:
    """Concept nodes the anchor links to: its own topics and methods, plus any
    programme concept its title or abstract mentions."""
    nodes = {f"{k}:{label}" for k, label in concepts_of(anchor)}
    words = method_key(f"{anchor['title']} {anchor['abstract']}")
    grams = {words[i:i + k] for k in range(1, 7) for i in range(len(words) - k + 1)}
    for c, d in g.nodes(data=True):
        if d["kind"] in ("method", "topic") and len(d["label"]) >= 4 \
                and not d.get("common") and method_key(d["label"]) in grams:
            nodes.add(c)
    return {c for c in nodes if c in g}


class TextIndex:
    """Typo-tolerant character TF-IDF over the corpus, fitted once per index."""

    def __init__(self, talks: list[dict]):
        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.mat = self.vec.fit_transform([doc(t) for t in talks])

    def sims(self, anchor: dict):
        return cosine_similarity(self.vec.transform([doc(anchor)]), self.mat)[0]


def score_all(anchor: dict, talks: list[dict], g: nx.Graph, cross,
              text_sim=None) -> dict[int, Scored]:
    n = len(talks)
    weights = idf(g, n)
    if text_sim is None:
        text_sim = TextIndex(talks).sims(anchor)
    a_nodes = anchor_concepts(anchor, g)
    total = sum(weights[c] for c in a_nodes) or 1.0
    # With no concept to compare, wording is the only evidence: weigh it fully
    # rather than halving every score by an empty concept term.
    text_weight = 0.5 if a_nodes else 1.0

    out: dict[int, Scored] = {}
    for i, t in enumerate(talks):
        if t["id"] == anchor["id"]:
            continue
        t_nodes = {f"{k}:{label}" for k, label in concepts_of(t)}
        shared = sorted(a_nodes & t_nodes, key=lambda c: (not c.startswith("method:"),
                                                          -weights[c], c))
        s = Scored(talk=t, text=float(text_sim[i]),
                   concept=sum(weights[c] for c in shared) / total,
                   shared=[g.nodes[c]["label"] for c in shared],
                   cross_domain=cross(t))
        s.score = min(1.0, text_weight * s.text + 0.5 * s.concept)
        bridges = [c for c in shared if not is_generic(g, c, n)]
        if bridges:
            s.bridge, s.bridge_kind = g.nodes[bridges[0]]["label"], g.nodes[bridges[0]]["kind"]
        out[t["id"]] = s
    return out


def walk_three_hops(scored: dict[int, Scored], g: nx.Graph, n_talks: int) -> None:
    """anchor -> strong talk -> shared method -> talk in another division.
    Upgrades a cross-division talk's unexpected score when the walk beats its
    direct score."""
    ranked = sorted(scored.values(), key=lambda s: (-s.score, s.talk["id"]))
    if not ranked or ranked[0].score <= 0:
        return
    seeds = [s for s in ranked[:SEEDS] if s.score >= 0.25 * ranked[0].score]
    for seed in seeds:
        for c in g.neighbors(f"talk:{seed.talk['id']}"):
            kind = g.nodes[c]["kind"]
            if kind not in BRIDGE_WEIGHT or is_generic(g, c, n_talks):
                continue
            for other in g.neighbors(c):
                if g.nodes[other]["kind"] != "talk":
                    continue
                s = scored.get(int(other.split(":")[1]))
                if s is None or s is seed or not s.cross_domain:
                    continue
                hop = 0.5 * seed.score * BRIDGE_WEIGHT[kind]
                direct = s.score * BRIDGE_WEIGHT.get(s.bridge_kind, 0) if s.bridge else 0
                if hop > direct and hop > (s.via or {}).get("_hop", 0):
                    s.hops, s.bridge, s.bridge_kind = 3, g.nodes[c]["label"], kind
                    s.via = {"id": seed.talk["id"], "title": seed.talk["title"], "_hop": hop}


def walk_deep(anchor: dict, scored: dict[int, Scored], g: nx.Graph, n_talks: int) -> None:
    """Multi-hop GraphRAG: Personalized PageRank from the anchor's concepts (and its
    closest talks by wording) over talk-concept links weighted by rarity. A talk in
    another division that the walk reaches strongly, through at least one concept,
    becomes an unexpected candidate explained by its cheapest graph path."""
    weights = idf(g, n_talks)
    top = max(weights.values(), default=1.0)
    h = nx.Graph()
    for u, v, d in g.edges(data=True):
        if d.get("rel") == "in_unit":
            continue
        c = u if g.nodes[u]["kind"] in ("method", "topic") else v
        rarity = weights[c] / top * (GENERIC_DAMPING if is_generic(g, c, n_talks) else 1.0)
        h.add_edge(u, v, w=d.get("w", 1.0) * rarity)
    seeds = [c for c in anchor_concepts(anchor, g) if c in h]
    if not seeds:
        return
    for c in seeds:
        h.add_edge("anchor", c, w=weights[c] / top)
    # Paths are explained through concepts only, so a deep pick is never "similar wording".
    costs, paths = nx.single_source_dijkstra(h, "anchor", weight=lambda u, v, d: 1.0 / d["w"])
    by_text = sorted(scored.values(), key=lambda s: -s.text)[:SEEDS]
    best_text = by_text[0].text if by_text and by_text[0].text > 0 else 1.0
    for s in by_text:
        if s.text > 0:
            h.add_edge("anchor", f"talk:{s.talk['id']}", w=0.5 * s.text / best_text)
    ppr = nx.pagerank(h, alpha=0.85, personalization={"anchor": 1.0}, weight="w")
    talk_ppr = {n: v for n, v in ppr.items() if n.startswith("talk:")}
    peak = max(talk_ppr.values(), default=0.0) or 1.0
    titles = {f"talk:{s.talk['id']}": s.talk["title"] for s in scored.values()}

    for s in scored.values():
        node = f"talk:{s.talk['id']}"
        path = paths.get(node)
        if not s.cross_domain or path is None or not 3 <= len(path) <= DEEP_MAX_HOPS + 1:
            continue
        deep = DEEP_WEIGHT * talk_ppr.get(node, 0.0) / peak
        if deep <= unexpected_score(s):
            continue
        steps = ["your talk"]
        for n in path[1:-1]:
            d = g.nodes[n]
            steps.append(f'"{titles.get(n, n)}"' if d["kind"] == "talk" else f"{d['kind']}: {d['label']}")
        steps.append("this talk")
        last = g.nodes[path[-2]]
        s.deep, s.deep_score, s.hops = steps, deep, len(path) - 1
        s.bridge, s.bridge_kind, s.via = last["label"], last["kind"], None


def unexpected_score(s: Scored) -> float:
    if s.deep is not None:
        return s.deep_score
    if not s.bridge:
        return 0.0
    if s.hops == 3:
        return s.via["_hop"]
    return s.score * BRIDGE_WEIGHT[s.bridge_kind]


def select(scored: dict[int, Scored]) -> list[Scored]:
    """Mark picks, return them first, then the nearest misses."""
    core = sorted((s for s in scored.values() if not s.cross_domain),
                  key=lambda s: (-s.score, s.talk["id"]))
    best = core[0].score if core else 0.0
    for s in core[:MAX_CORE]:
        s.match = s.score >= CORE_MIN and s.score >= CORE_RELATIVE * best
    surprise = sorted((s for s in scored.values() if s.cross_domain and unexpected_score(s) > 0),
                      key=lambda s: (-unexpected_score(s), s.talk["id"]))
    for s in surprise[:MAX_UNEXPECTED]:
        s.match = unexpected_score(s) >= UNEXPECTED_MIN
        s.score = max(s.score, unexpected_score(s))
    picks = [s for s in core + surprise if s.match]
    rest = sorted((s for s in scored.values() if not s.match),
                  key=lambda s: (-s.score, s.talk["id"]))[:KEEP_UNMATCHED]
    return picks + rest


def path(s: Scored) -> list[str]:
    """The graph path behind a pick, as readable steps."""
    if s.deep is not None:
        return s.deep
    if s.hops == 3:
        return ["your talk", f"\"{s.via['title']}\"", f"{s.bridge_kind}: {s.bridge}", "this talk"]
    via = s.bridge or (s.shared[0] if s.shared else "similar wording")
    return ["your talk", f"{s.bridge_kind or 'concept'}: {via}" if s.shared else via, "this talk"]


def template_why(s: Scored) -> str:
    units = "/".join(s.talk["units"]) or "another division"
    if s.cross_domain and s.deep is not None:
        middle = [p for p in s.deep[1:-1]]
        return (f"A different division ({units}), connected to your work in {s.hops} steps: "
                + " → ".join(middle) + ".")
    if s.cross_domain and s.hops == 3:
        return (f"A different division ({units}), but it uses {s.bridge}, as does "
                f"\"{s.via['title']}\", which closely matches your talk.")
    if s.cross_domain and s.bridge:
        return f"A different division ({units}), but it uses {s.bridge}, the same as your work."
    if s.shared:
        return "Shares " + ", ".join(s.shared[:3]) + " with your talk."
    return "Closely related to the wording of your abstract."
